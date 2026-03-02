package com.lara.dashboard.dto.tier2;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class Tier2FullDashboardDto {

    private String studentIdHashed;
    private ZpdStabilityDto zpdStability;
    private EmotionalRegulationDto emotionalRegulation;
    private LongitudinalEmotionsDto longitudinalEmotions;
    private PredictiveRiskEngineDto predictiveRiskEngine;
    private InterventionIntelligenceDto interventionIntelligence;
    private ConceptMasteryDeepDto conceptMasteryDeep;
    private IndependenceAnalysisDto independenceAnalysis;
    private LongitudinalLearningDto longitudinalLearning;
    private TimelineExplorerDto timelineExplorer;

    // 1. ZPD & Learning Stability
    @Data
    @Builder
    public static class ZpdStabilityDto {
        private Double zpdElasticityScore;
        private Double timeInOptimalZonePercentage;
        private Integer overshootEventsCount;
        private Integer undershootEventsCount;
        private List<Double> stabilityCurve;
        private Boolean driftDetectionAlert;
    }

    // 2. Emotional Regulation Analytics
    @Data
    @Builder
    public static class EmotionalRegulationDto {
        private Double volatilityIndex;
        private Double recoveryLatencySeconds;
        private Integer frustrationSpikeCount;
        private Double spikeDensityPerMinute;
        private List<Double> valenceTrendCurve;
        private List<Double> arousalTrendCurve;
        private List<HeatmapPoint> emotionalHeatmap;

        @Data
        @Builder
        public static class HeatmapPoint {
            private String time;
            private Double intensity;
        }
    }

    // 3. Longitudinal Emotional Trends
    @Data
    @Builder
    public static class LongitudinalEmotionsDto {
        private Double sevenSessionRollingVolatility;
        private Double fourteenSessionStabilityTrend;
        private List<Double> recoveryTimeImprovementCurve;
        private Boolean baselineShiftDetected;
        private List<Integer> escalationFrequencyTrend;
    }

    // 4. Predictive Risk Engine
    @Data
    @Builder
    public static class PredictiveRiskEngineDto {
        private Double frustrationEscalationRiskPct;
        private Double masteryStagnationProbPct;
        private List<Double> independenceTrajectoryProjection;
        private Double overScaffoldingRiskIndex;
        private ConfidenceBand confidenceBand;

        @Data
        @Builder
        public static class ConfidenceBand {
            private List<Double> lowerBound;
            private List<Double> upperBound;
        }
    }

    // 5. Intervention Intelligence
    @Data
    @Builder
    public static class InterventionIntelligenceDto {
        private List<ToolSuccess> successRatePerTool;
        private List<Double> toolEffectivenessOverTime;
        private Double habituationDecaySlope;
        private List<Integer> interventionFrequencyTrend;
        private Double dependencyRiskScore;
        private Double interventionTimingEfficiency;

        @Data
        @Builder
        public static class ToolSuccess {
            private String toolName;
            private Double successRate;
        }
    }

    // 6. Concept Mastery Deep View
    @Data
    @Builder
    public static class ConceptMasteryDeepDto {
        private List<ConceptMastery> masteryLevelPerConcept; // 0-5 scale
        private List<ScatterPoint> attemptsVsMasteryScatter;
        private Double advancementVelocity;
        private List<Double> difficultyProgressionCurve;
        private List<TimeMastery> timeToMasteryPerConcept;
        private List<String> conceptRegressionDetection;

        @Data
        @Builder
        public static class ConceptMastery {
            private String concept;
            private Double level; // 0-5
        }

        @Data
        @Builder
        public static class ScatterPoint {
            private Integer attempts;
            private Double masteryLevel;
            private String concept;
        }

        @Data
        @Builder
        public static class TimeMastery {
            private String concept;
            private Double hoursToMaster;
        }
    }

    // 7. Independence & Scaffolding Analysis
    @Data
    @Builder
    public static class IndependenceAnalysisDto {
        private Double independentResponseRatio;
        private Double assistanceFrequency;
        private Double promptDependencyIndex;
        private List<Double> autonomousCompletionTrend;
        private Double growthInSelfRegulation;
    }

    // 8. Longitudinal Learning Intelligence
    @Data
    @Builder
    public static class LongitudinalLearningDto {
        private Double rollingMasteryVelocity;
        private Double conceptRetentionStability;
        private Boolean crossConceptInterferenceDetected;
        private Boolean plateauDetection;
        private List<Phase> accelerationDecelerationPhases;

        public enum Phase { ACCELERATION, DECELERATION, PLATEAU }
    }

    // 9. Timeline Explorer
    @Data
    @Builder
    public static class TimelineExplorerDto {
        private List<TimelineEvent> scrubbableSessionTimeline;

        @Data
        @Builder
        public static class TimelineEvent {
            private String sessionTime;
            private EventType type;
            private String description;

            public enum EventType {
                FRUSTRATION_SPIKE, INTERVENTION_TRIGGER, CONCEPT_MASTERY
            }
        }
    }
}
