package com.lara.dashboard.service;

import com.lara.dashboard.dto.clinical.ClinicalDashboardDTO;
import com.lara.dashboard.model.SessionSummaryMetric;
import com.lara.dashboard.model.Student;
import com.lara.dashboard.model.ToolIntervention;
import com.lara.dashboard.repository.SessionSummaryMetricRepository;
import com.lara.dashboard.repository.StudentRepository;
import com.lara.dashboard.repository.ToolInterventionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ClinicalDashboardService {

    private final SessionSummaryMetricRepository sessionSummaryMetricRepository;
    private final StudentRepository studentRepository;
    private final ToolInterventionRepository toolInterventionRepository;

    /**
     * Aggregates the precomputed rollups into a chart-friendly DTO.
     * Caches the result per student to avoid database thrashing on dashboard refreshes.
     */
    @Cacheable(value = "clinicalDashboard", key = "#studentIdHashed")
    public Optional<ClinicalDashboardDTO> getClinicalDashboard(String studentIdHashed, int daysRange) {
        log.info("Fetching Clinical Dashboard for {}, range {} days", studentIdHashed, daysRange);
        
        Optional<Student> studentOpt = studentRepository.findByStudentIdHashed(studentIdHashed);
        if (studentOpt.isEmpty()) {
            return Optional.empty();
        }
        Student student = studentOpt.get();

        LocalDate end = LocalDate.now();
        LocalDate start = end.minusDays(daysRange);

        List<SessionSummaryMetric> metrics = sessionSummaryMetricRepository
                .findByChildIdHashedAndSummaryDateBetweenOrderBySummaryDateAsc(studentIdHashed, start, end);

        if (metrics.isEmpty()) {
            return Optional.of(buildEmptyResponse(student));
        }

        return Optional.of(mapToClinicalDto(student, metrics, start, end));
    }

    private ClinicalDashboardDTO mapToClinicalDto(Student student, List<SessionSummaryMetric> metrics, LocalDate start, LocalDate end) {
        List<String> labels = new ArrayList<>();
        List<Double> recoveryTimes = new ArrayList<>();
        List<Integer> frustrationCounts = new ArrayList<>();
        List<Double> volatilities = new ArrayList<>();
        List<Double> zpds = new ArrayList<>();

        DateTimeFormatter dtf = DateTimeFormatter.ISO_LOCAL_DATE;

        long sessionCount = 0;
        for (SessionSummaryMetric m : metrics) {
            labels.add(m.getSummaryDate().format(dtf));
            recoveryTimes.add(m.getRollingAvgRecoverySeconds() != null ? m.getRollingAvgRecoverySeconds() : 0.0);
            frustrationCounts.add(m.getRollingFrustrationSpikes() != null ? m.getRollingFrustrationSpikes() : 0);
            volatilities.add(m.getAverageVolatilityThatDay() != null ? m.getAverageVolatilityThatDay() : 0.0);
            zpds.add(m.getCumulativeTimeInZpdPercentage() != null ? m.getCumulativeTimeInZpdPercentage() : 0.0);
            if (m.getTotalSessionsThatDay() != null) {
                sessionCount += m.getTotalSessionsThatDay();
            }
        }

        // Calculate overall intervention effectiveness from the metrics array
        double totalSuccessRate = metrics.stream()
                .filter(m -> m.getInterventionSuccessRate() != null)
                .mapToDouble(SessionSummaryMetric::getInterventionSuccessRate)
                .average()
                .orElse(0.0);

        // Fetch top tools natively for this time period
        List<ToolIntervention> rawTools = toolInterventionRepository
                .findByChildIdHashedAndTimestampBetween(student.getStudentIdHashed(), start.atStartOfDay(), end.atTime(23, 59, 59));
        
        List<ClinicalDashboardDTO.ToolSuccess> topTools = rawTools.stream()
                .collect(Collectors.groupingBy(ToolIntervention::getToolName))
                .entrySet().stream()
                .map(e -> {
                    long usage = e.getValue().size();
                    double avgSuccess = e.getValue().stream()
                            .filter(t -> t.getOutcomeScore() != null)
                            .mapToDouble(ToolIntervention::getOutcomeScore)
                            .average()
                            .orElse(0.0);
                    return ClinicalDashboardDTO.ToolSuccess.builder()
                            .toolName(e.getKey())
                            .usageCount(usage)
                            .averageSuccessScore(avgSuccess)
                            .build();
                })
                .sorted((t1, t2) -> Double.compare(t2.getAverageSuccessScore(), t1.getAverageSuccessScore()))
                .limit(5)
                .collect(Collectors.toList());

        return ClinicalDashboardDTO.builder()
                .studentIdHashed(student.getStudentIdHashed())
                .studentName(student.getName())
                .demographic(ClinicalDashboardDTO.DemographicData.builder()
                        .age(student.getAge())
                        .totalSessions(sessionCount)
                        .build())
                .recoveryTimes(ClinicalDashboardDTO.TimeSeriesData.<Double>builder()
                        .timestamps(labels).values(recoveryTimes).build())
                .frustrationCounts(ClinicalDashboardDTO.TimeSeriesData.<Integer>builder()
                        .timestamps(labels).values(frustrationCounts).build())
                .volatilityIndices(ClinicalDashboardDTO.TimeSeriesData.<Double>builder()
                        .timestamps(labels).values(volatilities).build())
                .timeInZpdPercentages(ClinicalDashboardDTO.TimeSeriesData.<Double>builder()
                        .timestamps(labels).values(zpds).build())
                .interventionEffectiveness(ClinicalDashboardDTO.InterventionEffectiveness.builder()
                        .overallSuccessRate(totalSuccessRate)
                        .preferredTools(topTools)
                        .build())
                .build();
    }

    private ClinicalDashboardDTO buildEmptyResponse(Student student) {
        return ClinicalDashboardDTO.builder()
                .studentIdHashed(student.getStudentIdHashed())
                .studentName(student.getName())
                .demographic(ClinicalDashboardDTO.DemographicData.builder()
                        .age(student.getAge())
                        .totalSessions(0L)
                        .build())
                .recoveryTimes(ClinicalDashboardDTO.TimeSeriesData.<Double>builder()
                        .timestamps(List.of()).values(List.of()).build())
                .frustrationCounts(ClinicalDashboardDTO.TimeSeriesData.<Integer>builder()
                        .timestamps(List.of()).values(List.of()).build())
                .volatilityIndices(ClinicalDashboardDTO.TimeSeriesData.<Double>builder()
                        .timestamps(List.of()).values(List.of()).build())
                .timeInZpdPercentages(ClinicalDashboardDTO.TimeSeriesData.<Double>builder()
                        .timestamps(List.of()).values(List.of()).build())
                .interventionEffectiveness(ClinicalDashboardDTO.InterventionEffectiveness.builder()
                        .overallSuccessRate(0.0)
                        .preferredTools(List.of())
                        .build())
                .build();
    }
}
