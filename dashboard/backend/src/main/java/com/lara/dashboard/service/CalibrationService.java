package com.lara.dashboard.service;

import com.lara.dashboard.dto.CalibrationMetricsDto;
import com.lara.dashboard.model.CalibrationLog;
import com.lara.dashboard.repository.CalibrationLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;
import java.util.stream.Collectors;

@Service
@Slf4j
@RequiredArgsConstructor
public class CalibrationService {

    private final CalibrationLogRepository calibrationLogRepository;

    /**
     * Calculates the statistical calibration metrics for a user's specific prediction type.
     */
    public CalibrationMetricsDto getCalibrationMetrics(String childIdHashed, String predictionType) {
        LocalDateTime thirtyDaysAgo = LocalDateTime.now().minusDays(30);
        List<CalibrationLog> logs = calibrationLogRepository
                .findByChildIdHashedAndPredictionTypeAndTimestampAfterOrderByTimestampAsc(
                        childIdHashed, predictionType, thirtyDaysAgo
                );

        if (logs.isEmpty()) {
            return generateEmptyCalibration(childIdHashed, predictionType);
        }

        double brierScore = calculateBrierScore(logs);
        List<CalibrationMetricsDto.CalibrationBin> bins = computeReliabilityBins(logs, 10);
        double ece = calculateECE(bins, logs.size());
        double overconfidence = calculateOverconfidence(bins);

        return CalibrationMetricsDto.builder()
                .childIdHashed(childIdHashed)
                .predictionType(predictionType)
                .brierScore(brierScore)
                .expectedCalibrationError(ece)
                .overconfidenceIndex(overconfidence)
                .calibrationCurveData(bins)
                .build();
    }

    private double calculateBrierScore(List<CalibrationLog> logs) {
        double sumSqErr = 0.0;
        for (CalibrationLog log : logs) {
            double prob = log.getPredictedProbability();
            double actual = log.getActualOutcome();
            sumSqErr += Math.pow(prob - actual, 2);
        }
        return sumSqErr / logs.size();
    }

    private List<CalibrationMetricsDto.CalibrationBin> computeReliabilityBins(List<CalibrationLog> logs, int numBins) {
        Map<Integer, List<CalibrationLog>> groupedBins = new TreeMap<>();
        for (int i = 0; i < numBins; i++) groupedBins.put(i, new ArrayList<>());

        for (CalibrationLog log : logs) {
            int binIndex = Math.min((int) (log.getPredictedProbability() * numBins), numBins - 1);
            groupedBins.get(binIndex).add(log);
        }

        List<CalibrationMetricsDto.CalibrationBin> result = new ArrayList<>();
        double binSize = 1.0 / numBins;

        for (Map.Entry<Integer, List<CalibrationLog>> entry : groupedBins.entrySet()) {
            int i = entry.getKey();
            List<CalibrationLog> binLogs = entry.getValue();
            if (binLogs.isEmpty()) continue;

            double meanPred = binLogs.stream().mapToDouble(CalibrationLog::getPredictedProbability).average().orElse(0.0);
            double actualPositives = binLogs.stream().mapToInt(CalibrationLog::getActualOutcome).sum();
            double fractionOfPositives = actualPositives / binLogs.size();

            result.add(CalibrationMetricsDto.CalibrationBin.builder()
                    .binRange(String.format("%.1f-%.1f", i * binSize, (i + 1) * binSize))
                    .meanPredictedProbability(meanPred)
                    .actualFractionOfPositives(fractionOfPositives)
                    .sampleCount(binLogs.size())
                    .build());
        }
        return result;
    }

    private double calculateECE(List<CalibrationMetricsDto.CalibrationBin> bins, int totalSamples) {
        double ece = 0.0;
        for (CalibrationMetricsDto.CalibrationBin bin : bins) {
            double weight = (double) bin.getSampleCount() / totalSamples;
            ece += weight * Math.abs(bin.getMeanPredictedProbability() - bin.getActualFractionOfPositives());
        }
        return ece;
    }

    private double calculateOverconfidence(List<CalibrationMetricsDto.CalibrationBin> bins) {
         if (bins.isEmpty()) return 0.0;
         double confDiffSum = 0.0;
         int count = 0;
         for (CalibrationMetricsDto.CalibrationBin bin : bins) {
             if (bin.getMeanPredictedProbability() > 0.5) {
                 confDiffSum += (bin.getMeanPredictedProbability() - bin.getActualFractionOfPositives());
                 count++;
             }
         }
         return count == 0 ? 0.0 : (confDiffSum / count); // Positive if predicting too high
    }

    private CalibrationMetricsDto generateEmptyCalibration(String childIdHashed, String predictionType) {
        return CalibrationMetricsDto.builder().childIdHashed(childIdHashed).predictionType(predictionType)
                .brierScore(0.0).expectedCalibrationError(0.0).overconfidenceIndex(0.0)
                .calibrationCurveData(new ArrayList<>()).build();
    }
}
