package com.lara.dashboard.service;

import com.lara.dashboard.entity.*;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.format.DateTimeFormatter;
import java.util.*;
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
    private final ChildActivityPerformanceRepository activityPerformanceRepository;
    private final ChildCurriculumAssignmentRepository curriculumAssignmentRepository;
    private final ChildPreferenceRepository preferenceRepository;

    public Map<String, Object> getFullAnalytics(Long childId) {
        Child child = childRepository.findById(childId)
                .orElseThrow(() -> new RuntimeException("Child not found: " + childId));

        Map<String, Object> analytics = new LinkedHashMap<>();

        analytics.put("patient", buildPatientInfo(child));
        analytics.put("learningProgress", buildLearningProgress(childId));
        analytics.put("allConcepts", buildAllConcepts(childId));
        analytics.put("emotionalMetrics", buildEmotionalMetrics(childId));
        analytics.put("userProfiles", buildUserProfiles(childId));
        analytics.put("reinforcementMetrics", buildReinforcementMetrics(childId));
        analytics.put("visionSessionStats", buildVisionStats(childId));
        analytics.put("visionBehaviorCounts", buildVisionBehavior(childId));
        analytics.put("perceptionConfidence", buildPerceptionConfidence(childId));
        analytics.put("voiceProsodyMetrics", buildVoiceProsody(childId));
        analytics.put("vocalMoodDistribution", buildVocalMood(childId));
        analytics.put("totalEngagementSummary", buildEngagementSummary(childId));
        analytics.put("curriculumAssignments", buildCurriculumAssignments(childId));
        analytics.put("sessionHistory", buildSessionHistory(childId));

        return analytics;
    }

    private Map<String, Object> buildPatientInfo(Child child) {
        Map<String, Object> patient = new LinkedHashMap<>();
        patient.put("name", child.getName());
        patient.put("age", child.getAge());
        patient.put("diagnosis", child.getDiagnosis());
        patient.put("gradeLevel", child.getGradeLevel());

        List<ChildClinicianMapping> mappings = clinicianMappingRepository.findByChildId(child.getId());
        List<Map<String, Object>> clinicians = mappings.stream()
                .map(m -> {
                    Map<String, Object> c = new LinkedHashMap<>();
                    c.put("id", m.getClinician().getId());
                    c.put("name", m.getClinician().getName());
                    c.put("isPrimary", m.getIsPrimary());
                    return c;
                })
                .collect(Collectors.toList());
        patient.put("assignedClinicians", clinicians);
        return patient;
    }

    private Map<String, Object> buildLearningProgress(Long childId) {
        List<ChildLearningProgress> progress = learningProgressRepository.findByChildId(childId);
        if (progress.isEmpty()) {
            return Map.of("conceptName", "none", "masteryLevel", 0, "masteryPercentage", 0.0);
        }

        // Return the most recent / primary concept
        ChildLearningProgress primary = progress.get(0);
        Map<String, Object> lp = new LinkedHashMap<>();
        lp.put("conceptName", primary.getConceptName());
        lp.put("masteryLevel", primary.getMasteryLevel());
        lp.put("masteryPercentage", primary.getMasteryPercentage());
        lp.put("attemptCount", primary.getAttemptCount());
        lp.put("successRate", primary.getSuccessRate());
        lp.put("currentDifficulty", primary.getCurrentDifficulty());
        lp.put("masteryStatus", primary.getMasteryStatus());
        return lp;
    }

    private List<Map<String, Object>> buildAllConcepts(Long childId) {
        return learningProgressRepository.findByChildId(childId).stream()
                .map(lp -> {
                    Map<String, Object> concept = new LinkedHashMap<>();
                    concept.put("conceptName", lp.getConceptName());
                    concept.put("curriculumArea", lp.getCurriculumArea());
                    concept.put("masteryLevel", lp.getMasteryLevel());
                    concept.put("masteryPercentage", lp.getMasteryPercentage());
                    concept.put("successRate", lp.getSuccessRate());
                    concept.put("status", lp.getMasteryStatus() != null ? lp.getMasteryStatus().toLowerCase().replace(" ", "_") : "not_started");
                    return concept;
                })
                .collect(Collectors.toList());
    }

    private Map<String, Object> buildEmotionalMetrics(Long childId) {
        List<ChildEmotionalHistory> history = emotionalHistoryRepository.findTop7ByChildIdOrderByRecordedDateDesc(childId);
        Map<String, Object> em = new LinkedHashMap<>();

        int totalFrustration = history.stream().mapToInt(h -> h.getFrustrationCount() != null ? h.getFrustrationCount() : 0).sum();
        int totalRecovery = history.stream().mapToInt(h -> h.getRecoveryCount() != null ? h.getRecoveryCount() : 0).sum();
        int totalStability = history.stream().mapToInt(h -> h.getStabilityCount() != null ? h.getStabilityCount() : 0).sum();
        int stabilityIndex = totalStability + totalRecovery > 0
                ? (totalStability * 100) / (totalStability + totalFrustration + 1)
                : 50;

        em.put("frustrationCount", totalFrustration);
        em.put("recoveryCount", totalRecovery);
        em.put("neutralStabilityCount", totalStability);
        em.put("stabilityIndex", stabilityIndex);
        return em;
    }

    private Map<String, Object> buildUserProfiles(Long childId) {
        List<ChildPreference> prefs = preferenceRepository.findByChildId(childId);
        List<String> preferredTopics = prefs.stream()
                .filter(p -> p.getSentiment() == com.lara.dashboard.enums.TopicSentiment.LIKE)
                .map(ChildPreference::getTopic)
                .collect(Collectors.toList());

        Map<String, Object> profile = new LinkedHashMap<>();
        profile.put("preferredTopics", preferredTopics);
        profile.put("instructionDepth", 2); // Default
        return profile;
    }

    private Map<String, Object> buildReinforcementMetrics(Long childId) {
        List<ChildReinforcementMetrics> metrics = reinforcementRepository.findByChildId(childId);
        Map<String, Object> rm = new LinkedHashMap<>();

        for (ChildReinforcementMetrics m : metrics) {
            String key = m.getStyleName().replace("_", "");
            rm.put(key.substring(0, 1).toLowerCase() + key.substring(1), m.getSuccessRate());
        }

        metrics.stream().filter(ChildReinforcementMetrics::getIsPreferred).findFirst()
                .ifPresent(m -> rm.put("preferredStyle", m.getStyleName()));

        int totalEvents = metrics.stream().mapToInt(m -> m.getTotalEvents() != null ? m.getTotalEvents() : 0).sum();
        rm.put("totalEvents", totalEvents);
        return rm;
    }

    private Map<String, Object> buildVisionStats(Long childId) {
        Optional<ChildVisionMetricsEntity> latest = visionMetricsRepository.findTopByChildIdOrderByRecordedAtDesc(childId);
        Map<String, Object> vs = new LinkedHashMap<>();
        latest.ifPresent(v -> {
            vs.put("avgEngagementScore", v.getAvgEngagementScore());
            vs.put("avgGazeScore", v.getAvgGazeScore());
            vs.put("systemConfidence", v.getSystemConfidence());
        });
        return vs;
    }

    private Map<String, Object> buildVisionBehavior(Long childId) {
        Optional<ChildVisionMetricsEntity> latest = visionMetricsRepository.findTopByChildIdOrderByRecordedAtDesc(childId);
        Map<String, Object> vb = new LinkedHashMap<>();
        latest.ifPresent(v -> {
            vb.put("distractionFrames", v.getDistractionFrames());
            vb.put("focusedDuration", v.getFocusedDurationMinutes());
        });
        return vb;
    }

    private Map<String, Object> buildPerceptionConfidence(Long childId) {
        Optional<ChildVisionMetricsEntity> latest = visionMetricsRepository.findTopByChildIdOrderByRecordedAtDesc(childId);
        Map<String, Object> pc = new LinkedHashMap<>();
        latest.ifPresent(v -> {
            pc.put("faceConf", v.getFaceConfidence());
            pc.put("gestureConf", v.getGestureConfidence());
            pc.put("objectConf", v.getObjectConfidence());
        });
        return pc;
    }

    private Map<String, Object> buildVoiceProsody(Long childId) {
        Optional<ChildVoiceMetrics> latest = voiceMetricsRepository.findTopByChildIdOrderByRecordedAtDesc(childId);
        Map<String, Object> vp = new LinkedHashMap<>();
        latest.ifPresent(v -> {
            vp.put("speakingRate", v.getAvgSpeakingRateWpm());
            vp.put("volume", v.getAvgVolume());
            vp.put("stabilityScore", v.getSpeechStabilityScore());
        });
        return vp;
    }

    private Map<String, Object> buildVocalMood(Long childId) {
        Optional<ChildVoiceMetrics> latest = voiceMetricsRepository.findTopByChildIdOrderByRecordedAtDesc(childId);
        Map<String, Object> vm = new LinkedHashMap<>();
        latest.ifPresent(v -> {
            vm.put("neutral", v.getPctVocalNeutral() != null ? v.getPctVocalNeutral().doubleValue() / 100.0 : 0.0);
            vm.put("arousal", v.getPctVocalArousal() != null ? v.getPctVocalArousal().doubleValue() / 100.0 : 0.0);
            vm.put("withdrawal", v.getPctVocalWithdrawal() != null ? v.getPctVocalWithdrawal().doubleValue() / 100.0 : 0.0);
        });
        return vm;
    }

    private Map<String, Object> buildEngagementSummary(Long childId) {
        Optional<SessionAnalytics> latest = analyticsRepository.findTopByChildIdOrderByCreatedAtDesc(childId);
        Map<String, Object> es = new LinkedHashMap<>();
        latest.ifPresent(sa -> {
            es.put("totalEngagementAverage", sa.getTotalEngagementAverage());
            es.put("interactionContinuityScore", sa.getInteractionContinuityScore());

            // Get latest session duration
            sessionRepository.findTopByChild_IdOrderByEndTimeDesc(childId)
                    .ifPresent(s -> es.put("sessionDuration", s.getDurationSeconds() != null ? s.getDurationSeconds() / 60.0 : 0.0));
        });
        return es;
    }

    private List<Map<String, Object>> buildCurriculumAssignments(Long childId) {
        return curriculumAssignmentRepository.findByChildId(childId).stream()
                .map(ca -> {
                    Map<String, Object> assignment = new LinkedHashMap<>();
                    assignment.put("topicName", ca.getTopic().getName());
                    assignment.put("area", ca.getTopic().getArea());
                    assignment.put("status", ca.getStatus().name().toLowerCase());
                    assignment.put("assignedAt", ca.getAssignedAt() != null
                            ? ca.getAssignedAt().format(DateTimeFormatter.ofPattern("yyyy-MM-dd")) : null);
                    return assignment;
                })
                .collect(Collectors.toList());
    }

    private List<Map<String, Object>> buildSessionHistory(Long childId) {
        List<Session> sessions = sessionRepository.findAllByChild_Id(childId);
        return sessions.stream()
                .sorted(Comparator.comparing(Session::getStartTime, Comparator.nullsLast(Comparator.reverseOrder())))
                .limit(10)
                .map(s -> {
                    Map<String, Object> sh = new LinkedHashMap<>();
                    sh.put("sessionUuid", s.getSessionUuid());
                    sh.put("date", s.getStartTime() != null ? s.getStartTime().format(DateTimeFormatter.ofPattern("MMM dd, yyyy")) : null);
                    sh.put("duration", s.getDurationSeconds() != null ? (s.getDurationSeconds() / 60) + " min" : "0 min");
                    sh.put("peakDifficulty", s.getPeakDifficulty());
                    sh.put("dominantMood", s.getDominantMood());
                    sh.put("avgEngagement", s.getAvgEngagementScore());
                    sh.put("totalTurns", s.getTotalTurns());
                    return sh;
                })
                .collect(Collectors.toList());
    }
}
