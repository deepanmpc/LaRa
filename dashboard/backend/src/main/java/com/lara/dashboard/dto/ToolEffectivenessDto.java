package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ToolEffectivenessDto {
    private String childIdHashed;
    private List<DecayMetric> toolDecayMetrics;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class DecayMetric {
        private String toolId;
        private Double marginalEffectivenessSlope; // Negative implies diminishing returns
        private Double habituationRiskScore; // 0.0 to 1.0
        private Integer recommendedCooldownMinutes; // Recommended time to avoid this tool
    }
}
