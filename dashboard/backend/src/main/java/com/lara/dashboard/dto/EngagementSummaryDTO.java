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
public class EngagementSummaryDTO {
    private Integer focusScore;
    private Integer attentionSpanMinutes;
    private Integer taskCompletionRate;
    private String participationLevel;
    private String distractionFrequency;
    private Integer responsiveness;
    private Integer initiativeTaking;
    private Integer collaborationScore;
    private List<Map<String, Object>> weeklyFocusData;
    private List<Map<String, Object>> topActivities;
}
