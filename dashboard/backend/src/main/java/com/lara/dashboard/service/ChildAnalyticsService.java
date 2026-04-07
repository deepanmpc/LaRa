package com.lara.dashboard.service;

import com.lara.dashboard.entity.*;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ChildAnalyticsService {

    private final ChildRepository childRepository;
    private final SessionRepository sessionRepository;
    private final SessionAnalyticsRepository analyticsRepository;
    private final ChildLearningProgressRepository learningProgressRepository;
    private final ChildEmotionalHistoryRepository emotionalHistoryRepository;
    private final ChildEngagementHistoryRepository engagementHistoryRepository;
    private final ChildReinforcementMetricsRepository reinforcementRepository;
    private final ChildVoiceMetricsRepository voiceMetricsRepository;
    private final ChildVisionMetricsEntityRepository visionMetricsRepository;
    private final ChildClinicianMappingRepository clinicianMappingRepository;
    private final EmotionalMetricRepository emotionalMetricRepository;
    private final EngagementTimelineRepository engagementTimelineRepository;
    private final ZpdMetricRepository zpdMetricRepository;
    private final StudentLongitudinalMetricsRepository longitudinalRepository;
    private final SessionTurnMetricRepository turnMetricRepository;

    // Part 11 — Performance Optimization (In-memory cache)
    private final Map<Long, CachedAnalytics> analyticsCache = new ConcurrentHashMap<>();
    private static final long CACHE_DURATION_MS = 60000; // 60 seconds

    public Map<String, Object> getFullAnalytics(Long childId) {
        long now = System.currentTimeMillis();
        if (analyticsCache.containsKey(childId)) {
            CachedAnalytics cached = analyticsCache.get(childId);
            if (now - cached.timestamp < CACHE_DURATION_MS) {
                log.info("[Analytics] Returning cached data for child {}", childId);
                return cached.data;
            }
        }

        Child child = childRepository.findById(childId)
                .orElseThrow(() -> new RuntimeException("Child not found: " + childId));

        Map<String, Object> analytics = new LinkedHashMap<>();

        // Part 2 — Aggregation Queries
        analytics.put("patient", buildPatientInfo(child));
        analytics.put("cognitive", buildCognitiveSummary(childId));
        analytics.put("emotional", buildEmotionalSummary(childId, child));
        analytics.put("vision", buildVisionSummary(childId));
        analytics.put("reinforcement", buildReinforcementSummary(childId));
        analytics.put("sessions", buildSessionInsights(childId));
        analytics.put("longitudinal", buildLongitudinalSummary(childId));
        
        // Legacy support
        analytics.put("allConcepts", buildAllConcepts(childId));
        analytics.put("sessionHistory", buildSessionHistory(childId));

        analyticsCache.put(childId, new CachedAnalytics(now, analytics));
        return analytics;
    }

    public Map<String, Object> getOverview(Long childId) {
        Map<String, Object> full = getFullAnalytics(childId);
        Map<String, Object> overview = new LinkedHashMap<>();
        overview.put("profile", full.get("patient"));
        overview.put("cognitive_summary", full.get("cognitive"));
        overview.put("emotional_summary", full.get("emotional"));
        overview.put("vision_summary", full.get("vision"));
        overview.put("reinforcement_summary", full.get("reinforcement"));
        return overview;
    }

    public List<Map<String, Object>> getEngagementTimeline(Long childId) {
        // Fetch latest session for this child
        Optional<Session> latestSession = sessionRepository.findTopByChild_IdOrderByEndTimeDesc(childId);
        if (latestSession.isEmpty()) return Collections.emptyList();

        List<EngagementTimeline> timeline = engagementTimelineRepository.findBySessionIdOrderByMinuteIndexAsc(latestSession.get().getId());
        return timeline.stream().map(t -> {
            Map<String, Object> map = new LinkedHashMap<>();
            map.put("minute", t.getMinuteIndex());
            map.put("engagement", t.getAvgEngagement());
            map.put("state", t.getAttentionState());
            return map;
        }).collect(Collectors.toList());
    }

    private Map<String, Object> buildPatientInfo(Child child) {
        Map<String, Object> patient = new LinkedHashMap<>();
        patient.put("id", child.getId());
        patient.put("name", child.getName());
        patient.put("age", child.getAge());
        patient.put("diagnosis", child.getDiagnosis());
        patient.put("gradeLevel", child.getGradeLevel());
        patient.put("avatarColor", child.getAvatarColor());
        patient.put("statusBadge", child.getStatusBadge());
        patient.put("currentFocusArea", child.getCurrentFocusArea());
        return patient;
    }

    // Part 2 — Cognitive Development
    private Map<String, Object> buildCognitiveSummary(Long childId) {
        List<ChildLearningProgress> progress = learningProgressRepository.findByChildId(childId);
        Map<String, Object> cognitive = new LinkedHashMap<>();
        
        if (progress.isEmpty()) {
            cognitive.put("active_concept", "None");
            cognitive.put("mastery_percentage", 0.0);
            return cognitive;
        }

        ChildLearningProgress latest = progress.get(0); // Assuming sorted or pick most active
        cognitive.put("active_concept", latest.getConceptName());
        cognitive.put("mastery_level", latest.getMasteryLevel());
        cognitive.put("mastery_percentage", latest.getMasteryPercentage());
        cognitive.put("attempt_count", progress.stream().mapToInt(p -> p.getAttemptCount() != null ? p.getAttemptCount() : 0).sum());
        
        double avgSuccess = progress.stream()
            .mapToDouble(p -> p.getSuccessRate() != null ? p.getSuccessRate().doubleValue() : 0.0)
            .average().orElse(0.0);
        cognitive.put("success_rate", avgSuccess);
        cognitive.put("reliability", avgSuccess * 100); // task_completion_reliability
        
        cognitive.put("distribution", progress.stream().map(p -> {
            Map<String, Object> m = new HashMap<>();
            m.put("concept", p.getConceptName());
            m.put("mastery", p.getMasteryPercentage());
            return m;
        }).collect(Collectors.toList()));

        return cognitive;
    }

    // Part 2 — Emotional Stability
    private Map<String, Object> buildEmotionalSummary(Long childId, Child child) {
        String hash = java.util.Base64.getEncoder().encodeToString(String.valueOf(childId).getBytes()); // Simulating hash
        // In reality, SessionDBSync uses md5 hex first 16 chars
        try {
            java.security.MessageDigest md = java.security.MessageDigest.getInstance("MD5");
            byte[] array = md.digest(String.valueOf(childId).getBytes());
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 8; ++i) { sb.append(Integer.toHexString((array[i] & 0xFF) | 0x100).substring(1,3)); }
            hash = sb.toString();
        } catch (Exception e) {}

        LocalDateTime monthAgo = LocalDateTime.now().minusDays(30);
        List<EmotionalMetric> metrics = emotionalMetricRepository.findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(hash, monthAgo);
        
        Map<String, Object> emotional = new LinkedHashMap<>();
        if (metrics.isEmpty()) {
            emotional.put("regulation_index", 50);
            emotional.put("stability", "Stable");
            return emotional;
        }

        long frustrations = metrics.stream().filter(m -> m.getMoodScore() != null && m.getMoodScore() < 4).count();
        emotional.put("frustration_frequency", (double) frustrations / metrics.size());
        
        // regulation_index calculation
        double avgMood = metrics.stream().mapToInt(m -> m.getMoodScore() != null ? m.getMoodScore() : 5).average().orElse(5.0);
        emotional.put("regulation_index", avgMood * 10);
        emotional.put("baseline_stability", avgMood);
        
        List<Object[]> breakdown = emotionalMetricRepository.findEmotionBreakdown(hash, monthAgo);
        emotional.put("emotion_distribution", breakdown.stream().map(b -> {
            Map<String, Object> m = new HashMap<>();
            m.put("emotion", b[0]);
            m.put("count", b[1]);
            return m;
        }).collect(Collectors.toList()));

        return emotional;
    }

    // Part 2 — Vision & Perception
    private Map<String, Object> buildVisionSummary(Long childId) {
        Optional<ChildVisionMetricsEntity> latest = visionMetricsRepository.findTopByChildIdOrderByRecordedAtDesc(childId);
        Map<String, Object> vision = new LinkedHashMap<>();
        
        latest.ifPresent(v -> {
            vision.put("avg_engagement", v.getAvgEngagementScore());
            vision.put("focus_duration", v.getFocusedDurationMinutes());
            vision.put("distraction_rate", v.getDistractionFrames());
            vision.put("gaze_score", v.getAvgGazeScore());
            
            // Radar Chart Metrics
            Map<String, Object> radar = new LinkedHashMap<>();
            radar.put("ENGAGE", v.getAvgEngagementScore());
            radar.put("GAZE", v.getAvgGazeScore());
            radar.put("OBJECT", v.getObjectConfidence());
            radar.put("GESTURE", v.getGestureConfidence());
            radar.put("FACE", v.getFaceConfidence());
            radar.put("SYSTEM", v.getSystemConfidence());
            vision.put("radar", radar);
        });
        
        return vision;
    }

    // Part 2 — Reinforcement Intelligence
    private Map<String, Object> buildReinforcementSummary(Long childId) {
        List<ChildReinforcementMetrics> metrics = reinforcementRepository.findByChildId(childId);
        Map<String, Object> r = new LinkedHashMap<>();
        
        if (metrics.isEmpty()) return r;

        ChildReinforcementMetrics preferred = metrics.stream()
            .max(Comparator.comparing(rm -> rm.getSuccessRate() != null ? rm.getSuccessRate() : BigDecimal.ZERO))
            .get();
            
        r.put("primary_strategy", preferred.getStyleName());
        r.put("success_rate", preferred.getSuccessRate());
        r.put("total_events", metrics.stream().mapToInt(rm -> rm.getTotalEvents() != null ? rm.getTotalEvents() : 0).sum());
        
        r.put("effectiveness", metrics.stream().map(rm -> {
            Map<String, Object> m = new HashMap<>();
            m.put("strategy", rm.getStyleName());
            m.put("rate", rm.getSuccessRate());
            return m;
        }).collect(Collectors.toList()));

        return r;
    }

    // Part 2 — Session Insights
    private Map<String, Object> buildSessionInsights(Long childId) {
        Optional<SessionAnalytics> latest = analyticsRepository.findTopByChildIdOrderByCreatedAtDesc(childId);
        Map<String, Object> si = new LinkedHashMap<>();
        
        latest.ifPresent(sa -> {
            si.put("continuity", sa.getInteractionContinuityScore());
            si.put("initiative", sa.getInitiativeTakingScore());
            si.put("collaboration", sa.getCollaborationScore());
            si.put("responsiveness", sa.getResponsivenessScore());
        });
        
        return si;
    }

    // Part 2 — Longitudinal Analytics
    private Map<String, Object> buildLongitudinalSummary(Long childId) {
        Optional<StudentLongitudinalMetrics> metrics = longitudinalRepository.findByStudentId(String.valueOf(childId));
        Map<String, Object> l = new LinkedHashMap<>();
        
        metrics.ifPresent(m -> {
            l.put("mastery_velocity", m.getMasteryVelocity());
            l.put("frustration_risk", m.getFrustrationRiskScore());
            l.put("intervention_decay", m.getInterventionDecayIndex());
            l.put("independence_score", m.getIndependenceScore());
            l.put("engagement_volatility", m.getRollingVolatility7());
        });
        
        return l;
    }

    // Legacy helpers
    private List<Map<String, Object>> buildAllConcepts(Long childId) {
        return learningProgressRepository.findByChildId(childId).stream()
                .map(lp -> {
                    Map<String, Object> concept = new LinkedHashMap<>();
                    concept.put("conceptName", lp.getConceptName());
                    concept.put("masteryPercentage", lp.getMasteryPercentage());
                    concept.put("status", lp.getMasteryStatus());
                    return concept;
                }).collect(Collectors.toList());
    }

    private List<Map<String, Object>> buildSessionHistory(Long childId) {
        return sessionRepository.findAllByChild_Id(childId).stream()
                .sorted(Comparator.comparing(Session::getStartTime).reversed())
                .limit(10)
                .map(s -> {
                    Map<String, Object> map = new LinkedHashMap<>();
                    map.put("id", s.getId());
                    map.put("date", s.getStartTime().toString());
                    map.put("duration", s.getDurationSeconds());
                    map.put("engagement", s.getAvgEngagementScore());
                    map.put("mood", s.getDominantMood());
                    map.put("difficulty", s.getPeakDifficulty());
                    return map;
                }).collect(Collectors.toList());
    }

    @RequiredArgsConstructor
    private static class CachedAnalytics {
        private final long timestamp;
        private final Map<String, Object> data;
    }
}
