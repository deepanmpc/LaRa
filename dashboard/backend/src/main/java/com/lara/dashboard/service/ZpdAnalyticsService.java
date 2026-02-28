package com.lara.dashboard.service;

import com.lara.dashboard.dto.ZpdOverviewDto;
import com.lara.dashboard.model.ZpdMetric;
import com.lara.dashboard.repository.ZpdMetricRepository;
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
public class ZpdAnalyticsService {

    private final ZpdMetricRepository zpdMetricRepository;

    /**
     * Compute the ZPD Overview for the dashboard.
     * Involves calculating elasticity, moving averages, and aggregation.
     */
    public ZpdOverviewDto getZpdAnalytics(String childIdHashed, int daysRange) {
        LocalDateTime startDate = LocalDateTime.now().minusDays(daysRange);
        List<ZpdMetric> metrics = zpdMetricRepository.findByChildIdHashedAndTimestampBetween(
                childIdHashed, startDate, LocalDateTime.now()
        );

        if (metrics.isEmpty()) {
            return ZpdOverviewDto.builder().build(); // empty
        }

        // Aggregate by concept for mastery
        Map<String, List<ZpdMetric>> byConcept = metrics.stream()
                .collect(Collectors.groupingBy(ZpdMetric::getConceptId));

        List<ZpdOverviewDto.ConceptMasteryDto> masteryList = byConcept.entrySet().stream()
                .map(entry -> {
                    List<ZpdMetric> conceptMetrics = entry.getValue();
                    double maxMastery = conceptMetrics.stream()
                            .mapToDouble(ZpdMetric::getMasteryScore)
                            .max().orElse(0.0);
                    int attempts = conceptMetrics.stream()
                            .mapToInt(ZpdMetric::getEngagementFrequency)
                            .sum();
                            
                    return ZpdOverviewDto.ConceptMasteryDto.builder()
                            .conceptId(entry.getKey())
                            .masteryScore(maxMastery)
                            .totalAttempts(attempts)
                            .build();
                }).collect(Collectors.toList());

        // Calculate advancement velocity (simplified slope of mastery over time)
        double velocity = calculateVelocity(metrics);
        
        // ZPD Elasticity: How quickly does success recover after a difficulty spike?
        double elasticity = calculateElasticity(metrics);

        // Convert to Trend points (mocking grouping by day for chart)
        List<ZpdOverviewDto.ZpdTrendPoint> trends = metrics.stream()
                .map(m -> ZpdOverviewDto.ZpdTrendPoint.builder()
                        .timestamp(m.getTimestamp().toString())
                        .successRate(m.getMasteryScore() / (m.getDifficultyLevel() > 0 ? m.getDifficultyLevel() : 1))
                        .engagementFrequency(m.getEngagementFrequency())
                        .difficultyMA((double) m.getDifficultyLevel())
                        .build()
                ).collect(Collectors.toList());

        return ZpdOverviewDto.builder()
                .currentAdvancementVelocity(velocity)
                .averageElasticityScore(elasticity)
                .conceptMastery(masteryList)
                .historicalTrends(trends)
                .build();
    }

    private double calculateVelocity(List<ZpdMetric> metrics) {
        // Mock implementation: average change in mastery per item
        if(metrics.size() < 2) return 0.0;
        return (metrics.get(metrics.size()-1).getMasteryScore() - metrics.get(0).getMasteryScore()) / metrics.size();
    }

    private double calculateElasticity(List<ZpdMetric> metrics) {
        // Score based on recovering mastery at higher difficulty
        return metrics.stream()
                .mapToDouble(m -> (m.getMasteryScore() * 0.8) + (m.getDifficultyLevel() * 0.2))
                .average().orElse(0.0);
    }
}
