package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SystemPerformanceDto {
    private Long maxAggregationLatencyMs; // Worst case timing
    private Double averageCacheHitRate;
    private Integer alertOscillationEvents; // Rapid toggling of Alert Tiers suppressed
    private String systemStabilityStatus;
}
