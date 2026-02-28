package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SimulationResultDto {
    private String childIdHashed;
    private final String simulationDisclaimer = "Simulated Projection – Not Observed Data";
    
    // Projected Changes (Delts or absolute projected scores based on historical elasticity)
    private ProjectedMetric projectedFrustrationRisk;
    private ProjectedMetric projectedMasteryStagnation;
    private ProjectedMetric projectedIndependenceScore;

    @Data
    @Builder
    @NoArgsConstructor
    @AllArgsConstructor
    public static class ProjectedMetric {
        private Double projectedValue;
        private Double uncertaintyMargin; // Wider ci for more aggressive counterfactual shifts
        private Double lowerBound;
        private Double upperBound;
    }
}
