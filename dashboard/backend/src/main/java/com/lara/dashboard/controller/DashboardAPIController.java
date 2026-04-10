package com.lara.dashboard.controller;

import com.lara.dashboard.dto.*;
import com.lara.dashboard.service.ChildAnalyticsService;
import com.lara.dashboard.service.ClinicalIntelligenceService;
import com.lara.dashboard.service.KnowledgeGraphService;
import com.lara.dashboard.repository.SessionRepository;
import com.lara.dashboard.entity.Session;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.UserRepository;
import com.lara.dashboard.repository.ChildClinicianMappingRepository;
import com.lara.dashboard.enums.MappingStatus;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
public class DashboardAPIController {

    private final ChildAnalyticsService childAnalyticsService;
    private final AnalyticsController analyticsController;
    private final SessionRepository sessionRepository;
    private final ClinicalIntelligenceService clinicalIntelligenceService;
    private final KnowledgeGraphService knowledgeGraphService;
    private final com.lara.dashboard.repository.SessionTurnMetricRepository turnMetricRepository;
    private final com.lara.dashboard.service.PopulationAnalyticsService populationAnalyticsService;
    
    private final ChildRepository childRepository;
    private final ClinicianProfileRepository clinicianProfileRepository;
    private final UserRepository userRepository;
    private final ChildClinicianMappingRepository clinicianMappingRepository;

    private boolean isAuthorizedForChild(Long childId, Authentication auth) {
        String email = auth.getName();
        User user = userRepository.findByEmail(email).orElse(null);
        if (user == null) return false;
        
        if (user.getRole().name().equals("ROLE_ADMIN")) return true;
        
        if (user.getRole().name().equals("ROLE_CLINICIAN")) {
            Optional<ClinicianProfile> profile = clinicianProfileRepository.findByUserId(user.getId());
            Optional<Child> child = childRepository.findById(childId);
            if (child.isEmpty()) return false;

            // 1. Direct legacy profile link
            boolean directProfileLink = profile.isPresent() && 
                    child.get().getClinician() != null && 
                    child.get().getClinician().getId().equals(profile.get().getId());
            
            // 2. Direct user reference link
            boolean directUserLink = child.get().getAssignedClinician() != null && 
                    child.get().getAssignedClinician().getId().equals(user.getId());
            
            // 3. Mapping table link (most robust)
            boolean mappingLink = clinicianMappingRepository.findByChildIdAndClinicianIdAndStatus(
                    childId, user.getId(), MappingStatus.ACTIVE).isPresent();

            return directProfileLink || directUserLink || mappingLink;
        }
        
        if (user.getRole().name().equals("ROLE_FAMILY")) {
            Optional<Child> child = childRepository.findById(childId);
            return child.isPresent() && child.get().getParent() != null && 
                   child.get().getParent().getId().equals(user.getId());
        }
        
        return false;
    }

    @GetMapping("/children/{childId}/overview")
    @PreAuthorize("hasAnyAuthority('ROLE_CLINICIAN', 'ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getChildOverview(@PathVariable Long childId, Authentication auth) {
        if (!isAuthorizedForChild(childId, auth)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        return ResponseEntity.ok(childAnalyticsService.getOverview(childId));
    }

    @GetMapping("/children/{childId}/sessions")
    @PreAuthorize("hasAnyAuthority('ROLE_CLINICIAN', 'ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<List<Map<String, Object>>> getChildSessions(@PathVariable Long childId, Authentication auth) {
        if (!isAuthorizedForChild(childId, auth)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        List<Session> sessions = sessionRepository.findAllByChild_Id(childId);
        return ResponseEntity.ok(sessions.stream().map(s -> {
            Map<String, Object> m = new java.util.LinkedHashMap<>();
            m.put("id", s.getId());
            m.put("sessionUuid", s.getSessionUuid());
            m.put("startTime", s.getStartTime());
            m.put("endTime", s.getEndTime());
            m.put("duration", s.getDurationSeconds());
            m.put("mood", s.getDominantMood());
            m.put("engagement", s.getAvgEngagementScore());
            m.put("turns", s.getTotalTurns());
            m.put("difficulty", s.getPeakDifficulty());
            return m;
        }).collect(Collectors.toList()));
    }

    @GetMapping("/children/{childId}/analytics")
    @PreAuthorize("hasAnyAuthority('ROLE_CLINICIAN', 'ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getChildAnalytics(@PathVariable Long childId, Authentication auth) {
        if (!isAuthorizedForChild(childId, auth)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        return ResponseEntity.ok(childAnalyticsService.getFullAnalytics(childId));
    }

    @GetMapping("/children/{childId}/timeline")
    @PreAuthorize("hasAnyAuthority('ROLE_CLINICIAN', 'ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<List<Map<String, Object>>> getEngagementTimeline(@PathVariable Long childId, Authentication auth) {
        if (!isAuthorizedForChild(childId, auth)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        return ResponseEntity.ok(childAnalyticsService.getEngagementTimeline(childId));
    }

    @GetMapping("/children/{childId}/risk")
    @PreAuthorize("hasAnyAuthority('ROLE_CLINICIAN', 'ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getRiskSignals(@PathVariable Long childId, Authentication auth) {
        if (!isAuthorizedForChild(childId, auth)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        return ResponseEntity.ok(clinicalIntelligenceService.computeRiskSignals(childId));
    }

    @GetMapping("/children/{childId}/knowledge-graph")
    @PreAuthorize("hasAnyAuthority('ROLE_CLINICIAN', 'ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getKnowledgeGraph(@PathVariable Long childId, Authentication auth) {
        if (!isAuthorizedForChild(childId, auth)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();
        return ResponseEntity.ok(knowledgeGraphService.getKnowledgeGraph(childId));
    }

    @GetMapping("/sessions/{sessionId}/replay")
    @PreAuthorize("hasAnyAuthority('ROLE_CLINICIAN', 'ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<List<Map<String, Object>>> getSessionReplay(@PathVariable Long sessionId, Authentication auth) {
        Optional<Session> session = sessionRepository.findById(sessionId);
        if (session.isEmpty()) return ResponseEntity.notFound().build();
        if (!isAuthorizedForChild(session.get().getChild().getId(), auth)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();

        List<com.lara.dashboard.entity.SessionTurnMetric> turns = turnMetricRepository.findBySessionIdOrderByTurnNumberAsc(sessionId);
        return ResponseEntity.ok(turns.stream().map(t -> {
            Map<String, Object> m = new java.util.LinkedHashMap<>();
            m.put("turn_number", t.getTurnNumber());
            m.put("timestamp", t.getTimestamp());
            m.put("child_utterance", t.getChildUtterance());
            m.put("lara_response", t.getLaraResponse());
            m.put("engagement_score", t.getVisionEngagementScore());
            m.put("detected_mood", t.getDetectedMood());
            m.put("reinforcement_style", t.getReinforcementStyle());
            return m;
        }).collect(Collectors.toList()));
    }

    @GetMapping("/sessions/{sessionId}")
    @PreAuthorize("hasAnyAuthority('ROLE_CLINICIAN', 'ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<SessionSummaryResponse> getSession(@PathVariable Long sessionId, Authentication auth) {
        Optional<Session> session = sessionRepository.findById(sessionId);
        if (session.isEmpty()) return ResponseEntity.notFound().build();
        if (!isAuthorizedForChild(session.get().getChild().getId(), auth)) return ResponseEntity.status(HttpStatus.FORBIDDEN).build();

        return analyticsController.getSessionSummary(sessionId);
    }

    @GetMapping("/clinician/dashboard/{clinicianId}")
    public ResponseEntity<ClinicianDashboardResponse> getClinicianDashboard(@PathVariable Long clinicianId) {
        return analyticsController.getClinicianDashboard(clinicianId);
    }

    @GetMapping("/analytics/population")
    public ResponseEntity<Map<String, Object>> getPopulationAnalytics() {
        return ResponseEntity.ok(populationAnalyticsService.getPopulationAnalytics());
    }
}
