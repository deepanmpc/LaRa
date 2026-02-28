package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ModelHealthDto {
    private Double predictionAccuracy; // Prediction to real outcome success rate
    private Double calibrationTrend; // Positive slope indicates decaying stability
    private Double overrideImpactScore; // Impact magnitude of clinical overrides over AI selections
    private Boolean degradationFlag; // Triggered if accuracy drops below threshold or ECE scales
    private String healthSummary;
}
