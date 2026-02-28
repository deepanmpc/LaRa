package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class PredictiveRiskDto {
    private String childIdHashed;
    private Double frustrationRiskScore; // Z-score normalized
    private Double masteryStagnationProbability; // Plateau detection probability
    private Double interventionEscalationLikelihood;
    
    // Alert Tiering System (Tier 1: Soft, Tier 2: Mod, Tier 3: High)
    private Integer clinicalAlertTier;
    private String alertRationale;
}
