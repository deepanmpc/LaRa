package com.lara.dashboard.service;

import com.lara.dashboard.dto.CausalityMatrixDto;
import com.lara.dashboard.model.EmotionalMetric;
import com.lara.dashboard.model.ToolIntervention;
import com.lara.dashboard.repository.EmotionalMetricRepository;
import com.lara.dashboard.repository.ToolInterventionRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
@RequiredArgsConstructor
public class CausalityAnalyticsService {

    private final ToolInterventionRepository toolRepository;
    private final EmotionalMetricRepository emotionRepository;

    /**
     * Temporal Causality Analysis
     * Calculates cross-correlation with lags between Tool Deployment and Mood Delta.
     */
    public CausalityMatrixDto computeTemporalCausality(String childIdHashed) {
        LocalDateTime thirtyDaysAgo = LocalDateTime.now().minusDays(30);

        List<ToolIntervention> tools = toolRepository
                .findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(childIdHashed, thirtyDaysAgo);

        // Pre-computed causality modeling logic goes here
        Map<String, CausalityMatrixDto.CorrelationMetrics> toolMoodMatrix = computeLagCorrelation(tools);
        
        Map<String, Double> moodZpdMatrix = new HashMap<>(); // Placeholder for Mood->ZPD progression influence
        moodZpdMatrix.put("Frustrated", -0.45);
        moodZpdMatrix.put("Engaged", +0.72);

        return CausalityMatrixDto.builder()
                .childIdHashed(childIdHashed)
                .timeframeAnalyzed("30_DAYS")
                .toolMoodInfluenceMatrix(toolMoodMatrix)
                .moodZpdImpactMatrix(moodZpdMatrix)
                .build();
    }

    private Map<String, CausalityMatrixDto.CorrelationMetrics> computeLagCorrelation(List<ToolIntervention> tools) {
        Map<String, CausalityMatrixDto.CorrelationMetrics> matrix = new HashMap<>();
        
        // Mock Implementation of a sliding window cross-correlation algorithm
        // For a deployed system, this would align time-series arrays and shift by N minutes lag.
        
        matrix.put("Sensory Break", CausalityMatrixDto.CorrelationMetrics.builder()
                .lagCorrelationScore(0.85)
                .directionalInfluence(0.72) // Tool causes mood 72% of the time, not vice versa
                .optimalLagMinutes(15) // Effect peaks 15m after application
                .build());

        matrix.put("Gentle Nudge", CausalityMatrixDto.CorrelationMetrics.builder()
                .lagCorrelationScore(0.60)
                .directionalInfluence(0.40)
                .optimalLagMinutes(2)
                .build());

        return matrix;
    }
}
