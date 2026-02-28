package com.lara.dashboard.dto;

import lombok.Builder;
import lombok.Data;
import java.util.List;

@Data
@Builder
public class EmotionalOverviewDto {
    private Double emotionalVolatilityIndex;
    private Double avgRecoveryLatencyMinutes;
    private Double resilienceGrowthIndex;
    
    private List<MoodTrendPoint> heatmapCalendar;
    private List<FrustrationAlert> recentSpikes;

    @Data
    @Builder
    public static class MoodTrendPoint {
        private String date;
        private String dominantMood;
        private Integer spikeCount;
        private Double stabilityScore;
    }

    @Data
    @Builder
    public static class FrustrationAlert {
        private String timestamp;
        private String conceptId;
        private Integer streakLength;
        private String resolvedStatus;
    }
}
