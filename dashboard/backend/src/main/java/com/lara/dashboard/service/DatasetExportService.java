package com.lara.dashboard.service;

import com.lara.dashboard.entity.*;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.PrintWriter;
import java.io.StringWriter;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class DatasetExportService {

    private final SessionTurnMetricRepository turnMetricRepository;
    private final ChildVisionMetricsEntityRepository visionMetricsRepository;
    private final EmotionalMetricRepository emotionalMetricRepository;
    private final ToolInterventionRepository toolInterventionRepository;
    private final SessionAnalyticsRepository analyticsRepository;

    public String exportToCsv() {
        StringWriter sw = new StringWriter();
        PrintWriter pw = new PrintWriter(sw);

        // Header
        pw.println("session_id,turn_number,engagement_score,frustration_score,vision_attention_state,reinforcement_style,difficulty_level,intervention_success");

        List<SessionTurnMetric> turns = turnMetricRepository.findAll();
        for (SessionTurnMetric turn : turns) {
            pw.printf("%d,%d,%.2f,%.2f,%s,%s,%d,%s%n",
                turn.getSession().getId(),
                turn.getTurnNumber(),
                turn.getVisionEngagementScore() != null ? turn.getVisionEngagementScore() : 0.0,
                turn.getFrustrationPersistence() != null ? turn.getFrustrationPersistence() : 0.0,
                turn.getVisionAttentionState(),
                turn.getReinforcementStyle(),
                turn.getDifficultyLevel(),
                "N/A" // Simplified for now
            );
        }

        return sw.toString();
    }

    // Parquet export would typically require an external library like Avro/Parquet
    // For this prototype, we'll provide a placeholder or JSON-as-Parquet-proxy
    public byte[] exportToParquet() {
        // Placeholder: Returning CSV bytes since a full Parquet implementation 
        // requires complex dependency setup (Hadoop/Parquet)
        return exportToCsv().getBytes();
    }
}
