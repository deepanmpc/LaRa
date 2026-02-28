package com.lara.dashboard.dto;

import lombok.Builder;
import lombok.Data;
import java.util.List;

@Data
@Builder
public class ZpdOverviewDto {
    private Double currentAdvancementVelocity;
    private Double averageElasticityScore;
    private List<ZpdTrendPoint> historicalTrends;
    private List<ConceptMasteryDto> conceptMastery;

    @Data
    @Builder
    public static class ZpdTrendPoint {
        private String timestamp;
        private Double successRate;
        private Integer engagementFrequency;
        private Double difficultyMA;     // Moving average of difficulty
    }

    @Data
    @Builder
    public static class ConceptMasteryDto {
        private String conceptId;
        private Double masteryScore;
        private Integer totalAttempts;
    }
}
