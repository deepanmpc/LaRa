package com.lara.dashboard.service;

import com.lara.dashboard.model.ToolIntervention;
import com.lara.dashboard.repository.ToolInterventionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class ToolIntelligenceService {

    private final ToolInterventionRepository interventionRepository;

    public Map<String, Object> getToolAnalytics(String childIdHashed, int daysRange) {
        LocalDateTime startDate = LocalDateTime.now().minusDays(daysRange);
        List<ToolIntervention> interventions = interventionRepository.findByChildIdHashedAndTimestampBetween(
                childIdHashed, startDate, LocalDateTime.now()
        );

        if (interventions.isEmpty()) {
            return Map.of("loadIndex", 0.0, "successRate", 0.0);
        }

        // Calculate overarching success rate of tools
        double totalSuccess = interventions.stream()
                .filter(i -> i.getOutcomeScore() != null && i.getOutcomeScore() > 0.5)
                .count();
        double successRate = totalSuccess / interventions.size();

        // Calculate dependency risk (e.g. relying too heavily on high-intervention tools)
        double dependencyRisk = interventions.stream()
                .mapToDouble(i -> i.getInterventionDurationSecs() > 120 ? 1.0 : 0.5)
                .average().orElse(0.0);

        return Map.of(
                "successRate", successRate,
                "dependencyRiskScore", dependencyRisk,
                "totalInterventions", interventions.size(),
                "recentEvents", interventions.size() > 10 ? interventions.subList(0, 10) : interventions
        );
    }
}
