package com.lara.dashboard.service;

import com.lara.dashboard.entity.*;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class PopulationAnalyticsService {

    private final ChildRepository childRepository;
    private final ChildLearningProgressRepository learningProgressRepository;
    private final SessionRepository sessionRepository;
    private final ToolInterventionRepository toolInterventionRepository;

    public Map<String, Object> getPopulationAnalytics() {
        Map<String, Object> stats = new LinkedHashMap<>();

        List<Child> children = childRepository.findAll();
        
        // 1. Average Mastery by Age Group
        Map<String, Double> masteryByAge = children.stream()
            .collect(Collectors.groupingBy(
                c -> (c.getAge() != null ? (c.getAge() / 3 * 3) + "-" + (c.getAge() / 3 * 3 + 2) : "Unknown"),
                Collectors.averagingDouble(c -> {
                    List<ChildLearningProgress> progress = learningProgressRepository.findByChildId(c.getId());
                    return progress.stream().mapToDouble(p -> p.getMasteryPercentage() != null ? p.getMasteryPercentage().doubleValue() : 0.0).average().orElse(0.0);
                })
            ));
        stats.put("masteryByAgeGroup", masteryByAge);

        // 2. Engagement Distribution
        List<Session> allSessions = sessionRepository.findAll();
        Map<String, Long> engagementDist = allSessions.stream()
            .collect(Collectors.groupingBy(
                s -> {
                    double eng = s.getAvgEngagementScore() != null ? s.getAvgEngagementScore().doubleValue() : 0.0;
                    if (eng > 0.8) return "High";
                    if (eng > 0.4) return "Medium";
                    return "Low";
                },
                Collectors.counting()
            ));
        stats.put("engagementDistribution", engagementDist);

        // 3. Intervention Success Rates
        List<ToolIntervention> allInterventions = toolInterventionRepository.findAll();
        Map<String, Double> toolSuccess = allInterventions.stream()
            .collect(Collectors.groupingBy(
                ToolIntervention::getToolId,
                Collectors.averagingDouble(i -> "SUCCESS".equalsIgnoreCase(i.getOutcome()) ? 1.0 : 0.0)
            ));
        stats.put("interventionSuccessRates", toolSuccess);

        return stats;
    }
}
