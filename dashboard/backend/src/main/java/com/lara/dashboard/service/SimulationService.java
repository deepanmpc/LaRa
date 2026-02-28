package com.lara.dashboard.service;

import com.lara.dashboard.dto.SimulationRequestDto;
import com.lara.dashboard.dto.SimulationResultDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@Slf4j
@RequiredArgsConstructor
public class SimulationService {

    /**
     * Counterfactual Simulation Sandbox
     * Extrapolates predicted outcomes based on historical ZPD elasticity coefficients
     * if interventions, difficulty, or reinforcement logic were altered.
     */
    public SimulationResultDto runCounterfactualSimulation(String childIdHashed, SimulationRequestDto request) {
        
        // Mock Implementation of Elasticity Mathematics
        // In reality, this queries the PredictiveAnalyticsService for current EWMA baselines
        // and multiplies them against the user's historical delta elasticity.

        double baseFrustration = 0.65;
        double baseStagnation = 0.40;
        double baseIndependence = 0.70;

        // Difficulty shifts affect frustration (directly) and stagnation (inversely)
        double diffAdj = request.getDifficultyAdjustmentPercentage() != null ? request.getDifficultyAdjustmentPercentage() / 100.0 : 0.0;
        // Intervention frequency shifts affect independence (inversely) and frustration (inversely)
        double intAdj = request.getInterventionFrequencyAdjustment() != null ? request.getInterventionFrequencyAdjustment() / 100.0 : 0.0;

        double projFrustration = Math.max(0.0, Math.min(1.0, baseFrustration + (diffAdj * 0.8) - (intAdj * 0.4)));
        double projStagnation = Math.max(0.0, Math.min(1.0, baseStagnation - (diffAdj * 0.5)));
        double projIndependence = Math.max(0.0, Math.min(1.0, baseIndependence - (intAdj * 0.6) + (diffAdj * 0.2)));

        // Uncertainty grows non-linearly the further the counterfactual is from the factual mean
        double uncertaintyMultiplier = 1.0 + Math.abs(diffAdj) + Math.abs(intAdj);
        
        return SimulationResultDto.builder()
                .childIdHashed(childIdHashed)
                .projectedFrustrationRisk(buildProjectedMetric(projFrustration, 0.15 * uncertaintyMultiplier))
                .projectedMasteryStagnation(buildProjectedMetric(projStagnation, 0.10 * uncertaintyMultiplier))
                .projectedIndependenceScore(buildProjectedMetric(projIndependence, 0.20 * uncertaintyMultiplier))
                .build();
    }

    private SimulationResultDto.ProjectedMetric buildProjectedMetric(double projectedVal, double margin) {
        return SimulationResultDto.ProjectedMetric.builder()
                .projectedValue(projectedVal)
                .uncertaintyMargin(margin)
                .lowerBound(Math.max(0.0, projectedVal - margin))
                .upperBound(Math.min(1.0, projectedVal + margin))
                .build();
    }
}
