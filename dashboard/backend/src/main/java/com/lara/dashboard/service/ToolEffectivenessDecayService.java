package com.lara.dashboard.service;

import com.lara.dashboard.dto.ToolEffectivenessDto;
import com.lara.dashboard.model.ToolIntervention;
import com.lara.dashboard.repository.ToolInterventionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class ToolEffectivenessDecayService {

    private final ToolInterventionRepository toolRepository;

    /**
     * Assesses diminishing returns (habituation) of clinical tools used excessively on a child.
     */
    public ToolEffectivenessDto computeDecayMetrics(String childIdHashed) {
        LocalDateTime lookupDate = LocalDateTime.now().minusDays(30);
        List<ToolIntervention> interventions = toolRepository
                .findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(childIdHashed, lookupDate);

        Map<String, List<ToolIntervention>> groupedTools = interventions.stream()
                .collect(Collectors.groupingBy(ToolIntervention::getToolName));

        List<ToolEffectivenessDto.DecayMetric> decayMetrics = new ArrayList<>();

        for (Map.Entry<String, List<ToolIntervention>> entry : groupedTools.entrySet()) {
            decayMetrics.add(analyzeToolDecay(entry.getKey(), entry.getValue()));
        }

        return ToolEffectivenessDto.builder()
                .childIdHashed(childIdHashed)
                .toolDecayMetrics(decayMetrics)
                .build();
    }

    private ToolEffectivenessDto.DecayMetric analyzeToolDecay(String toolName, List<ToolIntervention> uses) {
        if (uses.size() < 3) {
            return ToolEffectivenessDto.DecayMetric.builder()
                    .toolId(toolName).marginalEffectivenessSlope(0.0)
                    .habituationRiskScore(0.0).recommendedCooldownMinutes(0).build();
        }

        // Simplistic linear regression on the outcome scores to find the slope
        double sumX = 0, sumY = 0, sumXY = 0, sumX2 = 0;
        int n = uses.size();
        for (int i = 0; i < n; i++) {
            double x = i;
            double y = uses.get(i).getOutcomeScore(); // Score post-intervention
            sumX += x;
            sumY += y;
            sumXY += x * y;
            sumX2 += x * x;
        }

        double slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
        
        // If slope is strongly negative, habituation risk is high
        double habituationRisk = slope < -0.05 ? Math.min(1.0, Math.abs(slope) * 10) : 0.0;
        int cooldown = habituationRisk > 0.6 ? 120 : (habituationRisk > 0.3 ? 30 : 0);

        return ToolEffectivenessDto.DecayMetric.builder()
                .toolId(toolName)
                .marginalEffectivenessSlope(slope)
                .habituationRiskScore(habituationRisk)
                .recommendedCooldownMinutes(cooldown)
                .build();
    }
}
