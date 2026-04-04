package com.lara.dashboard.controller;

import com.lara.dashboard.dto.*;
import com.lara.dashboard.entity.*;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/analytics")
@RequiredArgsConstructor
public class AnalyticsController {

    private final SessionRepository sessionRepository;
    private final SessionTurnMetricRepository turnMetricRepository;
    private final ChildVisionMetricsEntityRepository visionMetricsRepository;
    private final ChildVoiceMetricsRepository voiceMetricsRepository;
    private final ChildLearningProgressRepository learningProgressRepository;
    private final ChildReinforcementMetricsRepository reinforcementMetricsRepository;
    private final ChildRepository childRepository;

    @GetMapping("/sessions/{sessionId}")
    public ResponseEntity<SessionSummaryResponse> getSessionSummary(@PathVariable Long sessionId) {
        Session session = sessionRepository.findById(sessionId)
                .orElseThrow(() -> new RuntimeException("Session not found"));

        List<SessionTurnMetric> turns = turnMetricRepository.findBySessionIdOrderByTurnNumberAsc(sessionId);
        
        List<TurnMetricDTO> timeline = turns.stream()
                .map(t -> TurnMetricDTO.builder()
                        .turnNumber(t.getTurnNumber())
                        .childUtterance(t.getChildUtterance())
                        .laraResponse(t.getLaraResponse())
                        .mood(t.getDetectedMood())
                        .engagement(t.getVisionEngagementScore())
                        .strategy(t.getStrategyApplied())
                        .build())
                .collect(Collectors.toList());

        // Fetch metrics from secondary tables
        Optional<ChildVisionMetrics> vision = visionMetricsRepository.findBySessionId(sessionId);
        Optional<ChildVoiceMetrics> voice = voiceMetricsRepository.findBySessionId(sessionId);

        return ResponseEntity.ok(SessionSummaryResponse.builder()
                .id(session.getId())
                .sessionUuid(session.getSessionUuid())
                .startTime(session.getStartTime())
                .endTime(session.getEndTime())
                .durationSeconds(session.getDurationSeconds())
                .totalTurns(session.getTotalTurns())
                .dominantMood(session.getDominantMood())
                .avgEngagementScore(session.getAvgEngagementScore())
                .timeline(timeline)
                .visionMetrics(vision.isPresent() ? Map.of("avg_engagement", vision.get().getAvgEngagementScore()) : null)
                .voiceMetrics(voice.isPresent() ? Map.of("utterance_count", voice.get().getUtteranceCount()) : null)
                .build());
    }

    @GetMapping("/child/{childId}/history")
    public ResponseEntity<ChildHistoryResponse> getChildHistory(@PathVariable Long childId) {
        Child child = childRepository.findById(childId)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        List<Session> sessions = sessionRepository.findAllByChild_Id(childId);
        List<ChildLearningProgress> learning = learningProgressRepository.findByChildId(childId);

        return ResponseEntity.ok(ChildHistoryResponse.builder()
                .childId(child.getId())
                .childName(child.getName())
                .recentSessions(sessions.stream().map(s -> SessionBriefDTO.builder()
                        .id(s.getId())
                        .sessionUuid(s.getSessionUuid())
                        .startTime(s.getStartTime().toString())
                        .durationSeconds(s.getDurationSeconds())
                        .dominantMood(s.getDominantMood())
                        .avgEngagement(s.getAvgEngagementScore() != null ? s.getAvgEngagementScore().doubleValue() : 0.0)
                        .build()).collect(Collectors.toList()))
                .learningProgress(learning.stream().map(l -> Map.of(
                        "concept", (Object)l.getConceptName(),
                        "mastery", (Object)l.getMasteryPercentage(),
                        "attempts", (Object)l.getAttemptCount()
                )).collect(Collectors.toList()))
                .build());
    }

    @GetMapping("/clinician/{clinicianId}/dashboard")
    public ResponseEntity<ClinicianDashboardResponse> getClinicianDashboard(@PathVariable Long clinicianId) {
        List<Session> recentSessions = sessionRepository.findByChild_Clinician_Id(clinicianId);
        
        // This is a simplified aggregate for the purpose of the sync task
        return ResponseEntity.ok(ClinicianDashboardResponse.builder()
                .clinicianId(clinicianId)
                .children(new ArrayList<>()) # Would map children here
                .riskMetrics(Map.of("critical_alerts", 0))
                .build());
    }
}
