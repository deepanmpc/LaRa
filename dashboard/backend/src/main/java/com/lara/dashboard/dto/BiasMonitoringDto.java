package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class BiasMonitoringDto {
    // Ensuring privacy preservation; no raw demography is sent.
    // Tracking variances between mathematically grouped anonymized cohorts.
    
    private Double riskScoreVarianceIndex; // Should be as close to 0 as possible
    private Double interventionBiasIndex;
    private Boolean alertFrequencyImbalance;
    private Map<String, Double> cohortDeviationMap; // e.g. Cohort_Alpha: -0.02, Cohort_Beta: +0.03
    
    private String fairnessStatus;
}
