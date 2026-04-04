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
    private ChildProfileDTO childProfile;
    private SessionSummaryDTO sessionSummary;
    private EmotionalSummaryDTO emotionalMetrics;
    private EngagementSummaryDTO engagementMetrics;
}
