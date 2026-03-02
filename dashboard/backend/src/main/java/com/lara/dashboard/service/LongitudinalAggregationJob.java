package com.lara.dashboard.service;

import com.lara.dashboard.model.StudentLongitudinalMetrics;
import com.lara.dashboard.repository.StudentLongitudinalMetricsRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

/**
 * Part 2: POST-SESSION LONGITUDINAL INTELLIGENCE
 * Computes deep research-grade analytics safely asynchronously.
 * Never blocks the live child interaction.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class LongitudinalAggregationJob {

    private final StudentLongitudinalMetricsRepository metricsRepository;

    /**
     * Triggered on session completion event (e.g. via Spring ApplicationEventPublisher or manual call)
     */
    @Async
    public void runPostSessionAggregations(String studentIdHashed) {
        log.info("Starting heavy ASYNC longitudinal aggregation for student: {}", studentIdHashed);
        
        long start = System.currentTimeMillis();

        // Simulate heavy DB lookup & crunching:
        // 1. Load last 7 and 14 sessions
        // 2. Compute EWMA (Exponentially Weighted Moving Average)
        // 3. Compute Risk Forecasts & Decay modeling
        
        try {
            Thread.sleep(800); // Mocking heavy processing 
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        StudentLongitudinalMetrics aggregatedMetrics = StudentLongitudinalMetrics.builder()
                .studentId(studentIdHashed)
                .rollingVolatility7(3.8)
                .rollingVolatility14(4.1)
                .recoveryTrend(18.5)
                .masteryVelocity(1.2)
                .independenceScore(68.0)
                .interventionDecayIndex(0.02)
                .frustrationRiskScore(15.0)
                .confidenceBandLow(55.0)
                .confidenceBandHigh(75.0)
                .lastUpdated(LocalDateTime.now())
                .build();

        // 3. Store results in student_longitudinal_metrics table
        metricsRepository.save(aggregatedMetrics);

        long duration = System.currentTimeMillis() - start;
        log.info("Finished heavy ASYNC longitudinal aggregation for student: {} in {}ms", studentIdHashed, duration);
    }
}
