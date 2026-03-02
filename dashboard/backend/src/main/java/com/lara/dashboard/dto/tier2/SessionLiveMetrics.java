package com.lara.dashboard.dto.tier2;

import lombok.Builder;
import lombok.Data;

/**
 * Lightweight DTO for LIVE session analytics.
 * Spec Part 1: Kept in memory, updated every 5-10s, sub-100ms responses.
 * Never hits historical database or recomputes EWMA.
 */
@Data
@Builder
public class SessionLiveMetrics {
    private String sessionId;
    private String emotionalState;
    private Double shortWindowVolatility; // last 60-120 seconds
    private Integer frustrationCount;
    private Double engagementLevel;
    private Double zpdPosition;
    private String currentConcept;
    private Integer activeDifficultyLevel;
    private Long timestamp;
}
