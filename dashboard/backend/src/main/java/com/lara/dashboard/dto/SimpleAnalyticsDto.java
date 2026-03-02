package com.lara.dashboard.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class SimpleAnalyticsDto {
    private SessionSummary sessionSummary;
    private EmotionalOverview emotionalOverview;
    private InterventionSummary interventionSummary;
    private List<ConceptProgress> progressSnapshot;

    @Data
    @Builder
    public static class SessionSummary {
        private String learningFocus;
        private String emotionalStabilityStatus; // "Stable", "Slightly Challenging", "Needs Attention"
        private List<String> conceptsPracticed;
        private List<String> conceptsMastered;
        private String recommendedNextSteps;
    }

    @Data
    @Builder
    public static class EmotionalOverview {
        private String recoverySpeed; // "Fast", "Moderate", "Slow"
        private Integer frustrationSpikes;
        private String weekOverWeekTrend; // "Improved", "Similar", "Needs Monitoring"
    }

    @Data
    @Builder
    public static class InterventionSummary {
        private String primaryToolEffectiveness; // e.g. "Breathing exercise helped 3 out of 4 times."
        private String secondaryToolEffectiveness; 
        private String generalRecommendation; // e.g. "Consider rotating tools next week."
    }

    @Data
    @Builder
    public static class ConceptProgress {
        private String conceptName;
        private Integer masteryPercentage;
        private String trend; // "UP", "STABLE", "DOWN"
    }
}
