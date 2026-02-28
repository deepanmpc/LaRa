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
public class CalibrationMetricsDto {
    private String childIdHashed;
    private String predictionType;
    
    private Double brierScore; // Closer to 0 is better
    private Double expectedCalibrationError; // ECE, closer to 0 is better
    private Double overconfidenceIndex; // Positive = overconfident, Negative = underconfident
    
    // For reliability diagrams in Frontend
    private List<CalibrationBin> calibrationCurveData;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class CalibrationBin {
        private String binRange; // e.g., "0.0-0.1"
        private Double meanPredictedProbability;
        private Double actualFractionOfPositives;
        private Integer sampleCount;
    }
}
