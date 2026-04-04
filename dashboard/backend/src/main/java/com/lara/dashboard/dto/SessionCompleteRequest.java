package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionCompleteRequest {

    private String sessionUuid;
    private Long childId;
    private String startTime;
    private String endTime;
    private Integer durationSeconds;
    private Integer totalTurns;
    private Integer peakDifficulty;
    private String dominantMood;
    private BigDecimal avgMoodConfidence;
    private BigDecimal avgEngagementScore;
    private Integer totalInterventions;
    private Integer wakeWordTriggers;
    private Integer bargeInCount;

    private EmotionalData emotionalData;
    private EngagementData engagementData;
    private VisionData visionData;
    private VoiceData voiceData;
    private List<LearningProgressItem> learningProgress;
    private ReinforcementData reinforcementData;
    private List<ActivityItem> topActivities;
    private List<DifficultyTrajectoryItem> difficultyTrajectory;
    private List<TurnItem> turns;

    // ── Nested DTOs ──

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class EmotionalData {
        private Integer overallMoodScore;
        private String moodTrend;
        private String primaryEmotion;
        private Integer emotionStabilityScore;
        private String anxietyLevel;
        private Integer selfRegulationScore;
        private Integer positiveInteractions;
        private Integer challengingMoments;
        private BigDecimal pctHappy;
        private BigDecimal pctCalm;
        private BigDecimal pctFocused;
        private BigDecimal pctAnxious;
        private BigDecimal pctFrustrated;
        private BigDecimal pctSad;
        private BigDecimal pctNeutral;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class EngagementData {
        private Integer focusScore;
        private BigDecimal attentionSpanMinutes;
        private Integer taskCompletionRate;
        private String participationLevel;
        private String distractionFrequency;
        private Integer responsivenessScore;
        private Integer initiativeTakingScore;
        private Integer collaborationScore;
        private Integer weeklyGoalProgress;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class VisionData {
        private BigDecimal avgEngagementScore;
        private BigDecimal avgEngagementUiScore;
        private BigDecimal avgGazeScore;
        private BigDecimal systemConfidence;
        private BigDecimal faceConfidence;
        private BigDecimal gestureConfidence;
        private BigDecimal poseConfidence;
        private BigDecimal objectConfidence;
        private Integer totalDistractionFrames;
        private BigDecimal focusedDurationMinutes;
        private BigDecimal attentionFocusedPct;
        private BigDecimal attentionDistractedPct;
        private BigDecimal attentionAbsentPct;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class VoiceData {
        private Integer speakingRateWpm;
        private BigDecimal avgVolume;
        private BigDecimal speechStabilityScore;
        private Integer utteranceCount;
        private BigDecimal pctVocalNeutral;
        private BigDecimal pctVocalArousal;
        private BigDecimal pctVocalWithdrawal;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class LearningProgressItem {
        private String conceptName;
        private String curriculumArea;
        private Integer masteryLevel;
        private BigDecimal masteryPercentage;
        private BigDecimal successRate;
        private Integer attemptCount;
        private Integer successCount;
        private Integer currentDifficulty;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ReinforcementData {
        private Integer calmValidationSuccess;
        private Integer calmValidationTotal;
        private Integer praisedBasedSuccess;
        private Integer praisedBasedTotal;
        private Integer achievementBasedSuccess;
        private Integer achievementBasedTotal;
        private Integer playfulSuccess;
        private Integer playfulTotal;
        private String preferredStyle;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ActivityItem {
        private String name;
        private Integer score;
        private Integer completions;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DifficultyTrajectoryItem {
        private Integer turnNumber;
        private Integer before;
        private Integer after;
        private String direction;
        private String reason;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    public static class TurnItem {
        private Integer turnNumber;
        private String timestamp;
        private String childUtterance;
        private String laraResponse;
        private String detectedMood;
        private BigDecimal moodConfidence;
        private Integer difficultyLevel;
        private String strategyApplied;
        private String reinforcementStyle;
        private Integer promptBuildMs;
        private Integer inferenceMs;
        private Integer ttsMs;
        private Integer totalLatencyMs;
        private Boolean visionPresence;
        private String visionAttentionState;
        private BigDecimal visionEngagementScore;
        private String visionGesture;
        private Integer visionDistractionFrames;
    }
}
