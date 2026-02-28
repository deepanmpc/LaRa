package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CognitiveSummaryDto {
    private String dominantRiskTrend;
    private String recommendedAction;
    private String confidenceLevel;
    private String uncertaintyStatement;
    
    // Condensed clinical narrative
    private String structuredShortSummary;
}
