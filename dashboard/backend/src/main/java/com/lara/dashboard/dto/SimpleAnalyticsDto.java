package com.lara.dashboard.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class SimpleAnalyticsDto {
    private ActiveChildOverview activeChildOverview;
    private SessionSummary sessionSummary;
    private WeeklySnapshot weeklySnapshot;
    private EmotionalOverview emotionalOverview;
    private InterventionSummary interventionSummary;
    private List<ConceptProgress> progressSnapshot;
    private EngagementIndicator engagementIndicator;
    private List<String> milestonesAndAchievements;
    private List<String> recommendedNextSteps;
    private List<SessionHistoryCard> sessionHistory;

    @Data
    @Builder
    public static class ActiveChildOverview {
        private String childName;
        private Integer age;
        private String currentLearningTheme;
        private String lastSessionDate;
        private String overallStatusBadge; // "Doing Well", "Needs Extra Support", "Taking a Break"
    }

    @Data
    @Builder
    public static class SessionSummary {
        private String learningFocus;
        private String emotionalStabilityStatus; // "Stable", "Slightly Challenging", "Needs Attention"
        private List<String> conceptsPracticed;
        private List<String> conceptsMastered;
        private String aiNarrativeSummary; // Max 120 words plain English
    }

    @Data
    @Builder
    public static class WeeklySnapshot {
        private Integer sessionsCompleted;
        private String totalLearningTime;
        private Integer conceptsAdvanced;
        private String emotionalStabilityTrend; // "Improving", "Stable", "Slightly Challenging"
        private String weeklySummarySentence;
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
    public static class EngagementIndicator {
        private String engagementLevel; // "Highly Engaged", "Moderately Engaged", "Frequently Distracted"
        private String participationScore; // "Active", "Responsive", "Quiet"
    }

    @Data
    @Builder
    public static class InterventionSummary {
        private List<String> effectivenessStatements; // e.g., ["Breathing exercise helped 3 out of 4 times.", "Gentle nudges were effective."]
        private String generalRecommendation; // e.g., "Consider rotating tools this week."
    }

    @Data
    @Builder
    public static class ConceptProgress {
        private String conceptName;
        private Integer masteryPercentage;
        private String trend; // "UP", "STABLE", "DOWN"
    }

    @Data
    @Builder
    public static class SessionHistoryCard {
        private String date;
        private String duration;
        private String emotionalSummary;
        private String progressIndicator;
    }
}
