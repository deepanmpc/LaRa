package com.lara.dashboard.dto.simple;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class SimpleDashboardResponseDTO {
    private ChildOverviewDTO activeChildOverview;
    private SessionSummaryDTO sessionSummary;
    private EmotionalOverviewDTO emotionalOverview;
    private EngagementOverviewDTO engagementIndicator;
    private List<ProgressItemDTO> progressSnapshot;
    private InterventionSummaryDTO interventionSummary;
    private List<String> milestonesAndAchievements;
    private WeeklySnapshotDTO weeklySnapshot;
    private List<String> recommendedNextSteps;
    private List<SessionHistoryItemDTO> sessionHistory;
    
    @Data
    @Builder
    public static class ChildOverviewDTO {
        private String childName;
        private Integer age;
        private String currentLearningTheme;
        private String lastSessionDate;
        private String overallStatusBadge;
    }

    @Data
    @Builder
    public static class SessionSummaryDTO {
        private String learningFocus;
        private String emotionalStabilityStatus;
        private List<String> conceptsPracticed;
        private List<String> conceptsMastered;
        private String aiNarrativeSummary;
    }

    @Data
    @Builder
    public static class EmotionalOverviewDTO {
        private String recoverySpeed;
        private Integer frustrationSpikes;
        private String weekOverWeekTrend;
    }

    @Data
    @Builder
    public static class EngagementOverviewDTO {
        private String engagementLevel;
        private String participationScore;
    }

    @Data
    @Builder
    public static class ProgressItemDTO {
        private String conceptName;
        private Integer masteryPercentage;
        private String trend; // "UP", "STABLE", "DOWN" -> frontend maps "UP" / "DOWN" / "STABLE"
    }

    @Data
    @Builder
    public static class InterventionSummaryDTO {
        private List<String> effectivenessStatements;
        private String generalRecommendation;
    }

    @Data
    @Builder
    public static class WeeklySnapshotDTO {
        private Integer sessionsCompleted;
        private String totalLearningTime;
        private Integer conceptsAdvanced;
        private String emotionalStabilityTrend;
        private String weeklySummarySentence;
    }

    @Data
    @Builder
    public static class SessionHistoryItemDTO {
        private String date;
        private String duration;
        private String emotionalSummary;
        private String progressIndicator;
    }
}
