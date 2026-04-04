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
public class EmotionalSummaryDTO {
    private Integer overallMoodScore;
    private String moodTrend;
    private String primaryEmotion;
    private Integer emotionStability;
    private String anxietyLevel;
    private Integer selfRegulationScore;
    private Integer positiveInteractions;
    private Integer challengingMoments;
    private List<Map<String, Object>> weeklyMoodData;
    private Map<String, Integer> emotionBreakdown;
}
