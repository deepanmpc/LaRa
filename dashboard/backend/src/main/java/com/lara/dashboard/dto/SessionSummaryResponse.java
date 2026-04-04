package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionSummaryResponse {
    private Long id;
    private String sessionUuid;
    private LocalDateTime startTime;
    private LocalDateTime endTime;
    private Integer durationSeconds;
    private Integer totalTurns;
    private String dominantMood;
    private BigDecimal avgEngagementScore;
    private List<TurnMetricDTO> timeline;
    private Map<String, Object> visionMetrics;
    private Map<String, Object> voiceMetrics;
}

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class TurnMetricDTO {
    private Integer turnNumber;
    private String childUtterance;
    private String laraResponse;
    private String mood;
    private BigDecimal engagement;
    private String strategy;
}
