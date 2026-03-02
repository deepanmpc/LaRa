package com.lara.dashboard.dto.tier2;

import com.lara.dashboard.model.StudentLongitudinalMetrics;
import lombok.Builder;
import lombok.Data;

/**
 * Unified return object for Part 3: CLINICAL DASHBOARD ENDPOINT.
 * Merges high-speed live metrics (if session active) with cached heavy analytics.
 */
@Data
@Builder
public class HybridClinicalDashboardDto {
    private String studentId;
    
    // Present only if a session is currently active
    private SessionLiveMetrics liveMetrics;
    
    // Always present, fetched from Cache/Database asynchronously computed
    private StudentLongitudinalMetrics longitudinalMetrics;
}
