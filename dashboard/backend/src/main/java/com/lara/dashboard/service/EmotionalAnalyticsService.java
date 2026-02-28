package com.lara.dashboard.service;

import com.lara.dashboard.dto.EmotionalOverviewDto;
import com.lara.dashboard.model.EmotionalMetric;
import com.lara.dashboard.repository.EmotionalMetricRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.cache.annotation.Cacheable;

import java.time.LocalDateTime;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class EmotionalAnalyticsService {

    private final EmotionalMetricRepository emotionalMetricRepository;

    /**
     * Calculates combined emotional stability metrics based on JPA logs within a given date range.
     * Cached aggressively to spare heavy aggregate grouping functions.
     */
    @Cacheable(value = "emotionalMetrics", key = "#childIdHashed")
    public EmotionalOverviewDto getEmotionalMetrics(String childIdHashed, int daysRange) {
        LocalDateTime startDate = LocalDateTime.now().minusDays(daysRange);
        List<EmotionalMetric> metrics = emotionalMetricRepository.findByChildIdHashedAndTimestampBetween(
                childIdHashed, startDate, LocalDateTime.now()
        );

        if (metrics.isEmpty()) {
            return EmotionalOverviewDto.builder().build();
        }

        double volatility = calculateVolatility(metrics);
        double recoveryLatency = calculateAvgRecovery(metrics);
        double resilience = calculateResilience(metrics);

        List<EmotionalOverviewDto.MoodTrendPoint> heatmap = metrics.stream()
                .map(m -> EmotionalOverviewDto.MoodTrendPoint.builder()
                        .date(m.getTimestamp().toLocalDate().toString())
                        .dominantMood(m.getMoodState())
                        .spikeCount(m.getFrustrationStreak() > 2 ? 1 : 0)
                        .stabilityScore((double) m.getStabilityIndex())
                        .build())
                .collect(Collectors.toList());

        List<EmotionalOverviewDto.FrustrationAlert> alerts = metrics.stream()
                .filter(m -> m.getFrustrationStreak() > 2)
                .map(m -> EmotionalOverviewDto.FrustrationAlert.builder()
                        .timestamp(m.getTimestamp().toString())
                        .conceptId("VARIOUS") // Requires Session join in real impl
                        .streakLength(m.getFrustrationStreak())
                        .resolvedStatus(m.getStabilityIndex() > 1 ? "RESOLVED" : "ACTIVE")
                        .build())
                .collect(Collectors.toList());

        return EmotionalOverviewDto.builder()
                .emotionalVolatilityIndex(volatility)
                .avgRecoveryLatencyMinutes(recoveryLatency)
                .resilienceGrowthIndex(resilience)
                .heatmapCalendar(heatmap)
                .recentSpikes(alerts)
                .build();
    }

    private double calculateVolatility(List<EmotionalMetric> metrics) {
        // Standard deviation of rapid mood swings
        return metrics.stream().mapToDouble(m -> m.getFrustrationStreak() * 0.5).sum() / metrics.size();
    }

    private double calculateAvgRecovery(List<EmotionalMetric> metrics) {
        // Mock returning baseline duration
        return 2.5; // minutes
    }

    private double calculateResilience(List<EmotionalMetric> metrics) {
        // Mock growth index over recent weeks
        return 1.15; // +15% resilience
    }
}
