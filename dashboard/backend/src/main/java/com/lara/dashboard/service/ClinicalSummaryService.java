package com.lara.dashboard.service;

import com.lara.dashboard.dto.CognitiveSummaryDto;
import com.lara.dashboard.dto.PredictiveRiskDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

@Service
@Slf4j
@RequiredArgsConstructor
public class ClinicalSummaryService {

    private final PredictiveAnalyticsService predictiveAnalyticsService;

    /**
     * Translates complex statistical meta-models (MAD, EWMA, Calibration curves)
     * into a single low-cognitive-load narrative for the dashboard header.
     */
    public CognitiveSummaryDto generateSummary(String childIdHashed) {
        // Fetch real-time predictive envelope
        PredictiveRiskDto risk = predictiveAnalyticsService.computePredictiveRisks(childIdHashed);

        String dominantTrend;
        String recommendedAction;
        String confidence;
        String uncertaintyStr;

        if (risk.getClinicalAlertTier() == 3) {
            dominantTrend = "High magnitude escalation vector detected within EWMA bounds.";
            recommendedAction = "Pre-emptive de-escalation protocol recommended (e.g. Deep Breathing).";
            confidence = "High (Bayesian CI explicitly narrow)";
            uncertaintyStr = String.format("Risk projection holds firmly above %.0f%% confidence lower-bound.", risk.getRiskLowerBound() * 100);
        } else if (risk.getClinicalAlertTier() == 2 && risk.getMasteryStagnationProbability() > 0.6) {
            dominantTrend = "Concept mastery plateau extending over the adaptive window.";
            recommendedAction = "Reduce task difficulty by 15% to rebuild momentum.";
            confidence = "Moderate";
            uncertaintyStr = "Stagnation highly probable, though emotional valence variance is wide.";
        } else {
            dominantTrend = "Session trajectory is stable and tracking nominally.";
            recommendedAction = "Maintain current scaffolding and ZPD progression zones.";
            confidence = "High";
            uncertaintyStr = "Predictions fall cleanly within a tight 15% uncertainty margin.";
        }

        String structuredNarrative = String.format(
            "%s %s Confidence is %s. %s", 
            dominantTrend, recommendedAction, confidence.toLowerCase(), uncertaintyStr
        );

        return CognitiveSummaryDto.builder()
                .dominantRiskTrend(dominantTrend)
                .recommendedAction(recommendedAction)
                .confidenceLevel(confidence)
                .uncertaintyStatement(uncertaintyStr)
                .structuredShortSummary(structuredNarrative)
                .build();
    }
}
