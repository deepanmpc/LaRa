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
public class ClinicianDashboardResponse {
    private Long clinicianId;
    private List<ChildSummaryDTO> children;
    private Map<String, Object> riskMetrics;
    private EngagementSummaryDTO overallEngagement;
    private List<InterventionStatsDTO> interventionStats;
}

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class ChildSummaryDTO {
    private Long id;
    private String name;
    private Integer age;
    private String diagnosis;
    private String lastSessionAt;
    private String currentMood;
    private Double engagementTrend;
    private Boolean atRisk;
}

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class InterventionStatsDTO {
    private String styleName;
    private Integer totalUses;
    private Double successRateBest;
}
