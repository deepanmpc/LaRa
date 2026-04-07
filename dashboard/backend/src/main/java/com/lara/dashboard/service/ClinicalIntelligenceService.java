package com.lara.dashboard.service;

import com.lara.dashboard.dto.ChildAlert;
import com.lara.dashboard.entity.*;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.security.MessageDigest;
import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ClinicalIntelligenceService {

    private final EmotionalMetricRepository emotionalMetricRepository;
    private final ChildLearningProgressRepository learningProgressRepository;
    private final StudentLongitudinalMetricsRepository longitudinalRepository;
    private final ZpdMetricRepository zpdMetricRepository;
    private final ToolInterventionRepository toolInterventionRepository;
    private final SessionRepository sessionRepository;
    private final ClinicalAlertRepository clinicalAlertRepository;

    public Map<String, Object> computeRiskSignals(Long childId) {
        Map<String, Object> signals = new LinkedHashMap<>();
        String childIdHashed = hashChildId(childId);

        signals.put("frustrationRisk", detectFrustrationRisk(childId, childIdHashed));
        signals.put("engagementTrend", detectEngagementDecay(childId));
        signals.put("masteryVelocity", computeMasteryVelocity(childId));
        signals.put("zpdStatus", detectZpdDrift(childIdHashed));
        signals.put("interventionEffectiveness", analyzeInterventionEffectiveness(childIdHashed));
        
        // Step 5 — Emotional Volatility
        signals.put("emotionalVolatility", computeEmotionalVolatility(childIdHashed));

        // Step 8 — Generate & Persist Alerts
        List<ClinicalAlert> alerts = generateAndPersistAlerts(childId, signals);
        signals.put("alerts", alerts);

        return signals;
    }

    private String detectFrustrationRisk(Long childId, String childIdHashed) {
        LocalDateTime recent = LocalDateTime.now().minusDays(7);
        List<EmotionalMetric> emotionalMetrics = emotionalMetricRepository.findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(childIdHashed, recent);
        
        if (emotionalMetrics.isEmpty()) return "LOW";

        int frustrationStreak = 0;
        int maxStreak = 0;
        int frustrationCount = 0;
        
        for (EmotionalMetric m : emotionalMetrics) {
            if (m.getMoodScore() != null && m.getMoodScore() < 3) {
                frustrationStreak++;
                frustrationCount++;
                maxStreak = Math.max(maxStreak, frustrationStreak);
            } else {
                frustrationStreak = 0;
            }
        }

        double pctFrustrated = (double) frustrationCount / emotionalMetrics.size();
        
        double engagementDrop = 0.0;
        List<Session> recentSessions = sessionRepository.findAllByChild_Id(childId).stream()
                .sorted(Comparator.comparing(Session::getStartTime).reversed())
                .limit(5)
                .collect(Collectors.toList());
        
        if (recentSessions.size() >= 2) {
            double latestEng = recentSessions.get(0).getAvgEngagementScore() != null ? recentSessions.get(0).getAvgEngagementScore().doubleValue() : 0.0;
            double prevEng = recentSessions.get(1).getAvgEngagementScore() != null ? recentSessions.get(1).getAvgEngagementScore().doubleValue() : 0.0;
            if (prevEng > latestEng) {
                engagementDrop = (prevEng - latestEng) / prevEng;
            }
        }

        double riskScore = (maxStreak * 0.4) + (pctFrustrated * 0.3) + (engagementDrop * 0.3);
        
        if (riskScore > 0.7) return "HIGH";
        if (riskScore > 0.3) return "MEDIUM";
        return "LOW";
    }

    private String detectEngagementDecay(Long childId) {
        List<Session> sessions = sessionRepository.findAllByChild_Id(childId).stream()
                .sorted(Comparator.comparing(Session::getStartTime).reversed())
                .limit(10)
                .collect(Collectors.toList());

        if (sessions.size() < 5) return "STABLE";

        double latestAvg = sessions.stream().limit(2)
                .mapToDouble(s -> s.getAvgEngagementScore() != null ? s.getAvgEngagementScore().doubleValue() : 0.0)
                .average().orElse(0.0);
        
        double olderAvg = sessions.stream().skip(sessions.size() - 2)
                .mapToDouble(s -> s.getAvgEngagementScore() != null ? s.getAvgEngagementScore().doubleValue() : 0.0)
                .average().orElse(0.0);

        if (olderAvg > 0 && (olderAvg - latestAvg) / olderAvg > 0.20) {
            return "DECAYING";
        }
        
        return "STABLE";
    }

    private String computeMasteryVelocity(Long childId) {
        List<ChildLearningProgress> progress = learningProgressRepository.findByChildId(childId);
        if (progress.isEmpty()) return "NORMAL";

        double avgMastery = progress.stream()
            .mapToDouble(p -> p.getMasteryPercentage() != null ? p.getMasteryPercentage().doubleValue() : 0.0)
            .average().orElse(0.0);
        
        if (avgMastery > 80) return "FAST";
        if (avgMastery < 30) return "SLOW";
        return "NORMAL";
    }

    private Double computeEmotionalVolatility(String childIdHashed) {
        List<EmotionalMetric> metrics = emotionalMetricRepository.findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(childIdHashed, LocalDateTime.now().minusDays(30));
        if (metrics.size() < 5) return 0.0;

        double avg = metrics.stream()
            .mapToDouble(m -> m.getMoodScore() != null ? m.getMoodScore() : 5.0)
            .average().orElse(5.0);
        
        double sumSq = metrics.stream()
            .mapToDouble(m -> Math.pow((m.getMoodScore() != null ? m.getMoodScore() : 5.0) - avg, 2))
            .sum();
            
        return Math.sqrt(sumSq / metrics.size());
    }

    private String detectZpdDrift(String childIdHashed) {
        LocalDateTime recent = LocalDateTime.now().minusDays(7);
        List<ZpdMetric> zpdMetrics = zpdMetricRepository.findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(childIdHashed, recent);
        
        if (zpdMetrics.isEmpty()) return "OPTIMAL";

        double avgZpd = zpdMetrics.stream().mapToInt(ZpdMetric::getScore).average().orElse(5.0);
        
        if (avgZpd < 3) return "DIFFICULTY_TOO_HIGH";
        if (avgZpd > 8) return "DIFFICULTY_TOO_LOW";
        
        return "OPTIMAL";
    }

    private Map<String, Object> analyzeInterventionEffectiveness(String childIdHashed) {
        List<ToolIntervention> interventions = toolInterventionRepository.findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(childIdHashed, LocalDateTime.now().minusDays(30));
        
        Map<String, List<ToolIntervention>> grouped = interventions.stream()
                .collect(Collectors.groupingBy(ToolIntervention::getToolId));

        Map<String, Object> effectiveness = new LinkedHashMap<>();
        grouped.forEach((tool, list) -> {
            long success = list.stream().filter(i -> "SUCCESS".equalsIgnoreCase(i.getOutcome())).count();
            effectiveness.put(tool, (double) success / list.size());
        });

        return effectiveness;
    }

    private List<ClinicalAlert> generateAndPersistAlerts(Long childId, Map<String, Object> signals) {
        List<ClinicalAlert> activeAlerts = new ArrayList<>();

        if ("HIGH".equals(signals.get("frustrationRisk"))) {
            activeAlerts.add(createAlert(childId, "HIGH_FRUSTRATION_RISK", "CRITICAL", "High frustration detected."));
        }

        if ("DECAYING".equals(signals.get("engagementTrend"))) {
            activeAlerts.add(createAlert(childId, "ENGAGEMENT_DECAY", "WARNING", "Engagement decline detected."));
        }

        if ((Double)signals.get("emotionalVolatility") > 2.0) {
            activeAlerts.add(createAlert(childId, "HIGH_VOLATILITY", "WARNING", "Emotional volatility is high."));
        }

        if (signals.get("zpdStatus").toString().startsWith("DIFFICULTY")) {
            activeAlerts.add(createAlert(childId, "ZPD_MISMATCH", "WARNING", "ZPD drift: " + signals.get("zpdStatus")));
        }

        return clinicalAlertRepository.saveAll(activeAlerts);
    }

    private ClinicalAlert createAlert(Long childId, String type, String severity, String msg) {
        return ClinicalAlert.builder()
                .childId(childId)
                .alertType(type)
                .severity(severity)
                .message(msg)
                .resolved(false)
                .build();
    }

    private String hashChildId(Long childId) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] array = md.digest(String.valueOf(childId).getBytes());
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 8; ++i) { sb.append(Integer.toHexString((array[i] & 0xFF) | 0x100).substring(1,3)); }
            return sb.toString();
        } catch (Exception e) {
            return String.valueOf(childId);
        }
    }
}
