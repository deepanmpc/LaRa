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
public class FamilyDashboardResponse {
    private Map<String, Object> childProfile;
    private Map<String, Object> sessionSummary;
    private Map<String, Object> emotionalMetrics;
    private Map<String, Object> engagementMetrics;
}
