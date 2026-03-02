package com.lara.dashboard.dto.clinical;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class ClinicalDashboardDTO {

    private String studentIdHashed;
    private String studentName;
    private DemographicData demographic;
    
    // Time-series arrays (chart-ready payloads)
    private TimeSeriesData<Double> recoveryTimes;
    private TimeSeriesData<Integer> frustrationCounts;
    private TimeSeriesData<Double> volatilityIndices;
    private TimeSeriesData<Double> timeInZpdPercentages;

    // Aggregates
    private InterventionEffectiveness interventionEffectiveness;

    @Data
    @Builder
    public static class DemographicData {
        private Integer age;
        private Long totalSessions;
    }

    @Data
    @Builder
    public static class TimeSeriesData<T> {
        private List<String> timestamps; // ISO-8601 Date strings
        private List<T> values;
    }

    @Data
    @Builder
    public static class InterventionEffectiveness {
        private Double overallSuccessRate;
        private List<ToolSuccess> preferredTools;
    }

    @Data
    @Builder
    public static class ToolSuccess {
        private String toolName;
        private Long usageCount;
        private Double averageSuccessScore;
    }
}
