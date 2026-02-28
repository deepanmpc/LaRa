package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CausalityMatrixDto {
    private String childIdHashed;
    private String timeframeAnalyzed;
    
    // Key: Tool Name (e.g., "Deep Breathing")
    // Value: Correlation Metrics
    private Map<String, CorrelationMetrics> toolMoodInfluenceMatrix;
    
    // Key: Emotion State Map
    // Value: Impact on ZPD 
    private Map<String, Double> moodZpdImpactMatrix;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CorrelationMetrics {
        private Double lagCorrelationScore; // -1.0 to 1.0
        private Double directionalInfluence; // Strength of CAUSALITY not just correlation
        private Integer optimalLagMinutes; // E.g., Tool effect peaks at 15m delay
    }
}
