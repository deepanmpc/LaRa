package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SystemIntegrityDto {
    private Double confidenceDecayRate;
    private Double distributionDriftMagnitude;
    private Integer recentOverridesLimitSpike;
    private String integrityStatus; // "NOMINAL", "WARNING_DRIFT", "CRITICAL_DECAY"
}
