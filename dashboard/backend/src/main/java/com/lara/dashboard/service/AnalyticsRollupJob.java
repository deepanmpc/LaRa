package com.lara.dashboard.service;

import com.lara.dashboard.model.EmotionalMetric;
import com.lara.dashboard.model.SessionSummaryMetric;
import com.lara.dashboard.model.Student;
import com.lara.dashboard.model.ToolIntervention;
import com.lara.dashboard.repository.EmotionalMetricRepository;
import com.lara.dashboard.repository.SessionSummaryMetricRepository;
import com.lara.dashboard.repository.StudentRepository;
import com.lara.dashboard.repository.ToolInterventionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Slf4j
@Service
@RequiredArgsConstructor
public class AnalyticsRollupJob {

    private final StudentRepository studentRepository;
    private final EmotionalMetricRepository emotionalMetricRepository;
    private final ToolInterventionRepository toolInterventionRepository;
    private final SessionSummaryMetricRepository sessionSummaryMetricRepository;

    /**
     * Runs every night at 2:00 AM.
     * Computes the rolling averages for the previous day (or today if triggered manually).
     */
    @Scheduled(cron = "0 0 2 * * ?")
    @Transactional
    public void performNightlyRollup() {
        log.info("Starting nightly Analytics Rollup Job...");
        LocalDate targetDate = LocalDate.now().minusDays(1);
        List<Student> allStudents = studentRepository.findAll();

        for (Student student : allStudents) {
            aggregateMetricsForStudentAndDate(student.getStudentIdHashed(), targetDate);
        }
        log.info("Finished nightly Analytics Rollup Job.");
    }

    /**
     * Can be called independently, e.g., right after a session closes if we want immediate rolling updates.
     */
    @Transactional
    public void aggregateMetricsForStudentAndDate(String studentIdHashed, LocalDate date) {
        LocalDateTime startOfDay = date.atStartOfDay();
        LocalDateTime endOfDay = date.atTime(23, 59, 59);
        LocalDateTime sevenDaysAgo = startOfDay.minusDays(7);

        // Fetch 7-day window data for rolling logic
        List<EmotionalMetric> rollingEmotions = emotionalMetricRepository.findByChildIdHashedAndTimestampBetween(studentIdHashed, sevenDaysAgo, endOfDay);
        List<ToolIntervention> rollingTools = toolInterventionRepository.findByChildIdHashedAndTimestampBetween(studentIdHashed, sevenDaysAgo, endOfDay);

        // Fetch just today's data for discrete logging 
        List<EmotionalMetric> todayEmotions = rollingEmotions.stream()
                .filter(e -> !e.getTimestamp().isBefore(startOfDay))
                .toList();

        if (rollingEmotions.isEmpty() && rollingTools.isEmpty()) {
            return; // Nothing to rollup
        }

        double avgRecoverySecs = 0.0;
        int successfulTools = 0;
        int totalTools = rollingTools.size();

        for (ToolIntervention tool : rollingTools) {
            if (tool.getInterventionDurationSecs() != null) {
                avgRecoverySecs += tool.getInterventionDurationSecs();
            }
            if (tool.getOutcomeScore() != null && tool.getOutcomeScore() > 0.5) { // Simple mock threshold
                successfulTools++;
            }
        }
        if (totalTools > 0) avgRecoverySecs /= totalTools;
        double successRate = totalTools > 0 ? ((double) successfulTools / totalTools) * 100 : 0.0;

        int rollingFrustrationCount = (int) rollingEmotions.stream()
                .filter(e -> e.getFrustrationScore() != null && e.getFrustrationScore() > 0.7)
                .count();

        double averageVolatilityToday = todayEmotions.stream()
                .filter(e -> e.getStabilityIndex() != null)
                .mapToInt(e -> e.getStabilityIndex())
                .average()
                .orElse(0.0);

        SessionSummaryMetric metric = sessionSummaryMetricRepository.findByChildIdHashedAndSummaryDate(studentIdHashed, date)
                .orElse(new SessionSummaryMetric());

        metric.setChildIdHashed(studentIdHashed);
        metric.setSummaryDate(date);
        metric.setRollingAvgRecoverySeconds(avgRecoverySecs);
        metric.setRollingFrustrationSpikes(rollingFrustrationCount);
        metric.setInterventionSuccessRate(successRate);
        metric.setAverageVolatilityThatDay(averageVolatilityToday);
        // Mock ZPD percentage 
        metric.setCumulativeTimeInZpdPercentage(75.0); 

        sessionSummaryMetricRepository.save(metric);
        log.debug("Saved rollup for student {} for date {}", studentIdHashed, date);
    }
}
