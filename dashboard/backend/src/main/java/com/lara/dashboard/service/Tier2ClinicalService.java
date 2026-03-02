package com.lara.dashboard.service;

import com.lara.dashboard.dto.tier2.Tier2FullDashboardDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.util.List;

import com.lara.dashboard.dto.tier2.HybridClinicalDashboardDto;
import com.lara.dashboard.dto.tier2.SessionLiveMetrics;
import com.lara.dashboard.model.StudentLongitudinalMetrics;
import com.lara.dashboard.repository.StudentLongitudinalMetricsRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.List;

@Service
@Slf4j
@RequiredArgsConstructor
public class Tier2ClinicalService {

    private final StudentLongitudinalMetricsRepository longitudinalMetricsRepository;
    private final LiveSessionService liveSessionService;

    /**
     * Requirement Part 3: Hybrid Endpoint.
     * Merges Post-Session Longitudinal Intelligence (Cached) with Live Session Metrics.
     */
    public HybridClinicalDashboardDto getHybridDashboard(String studentIdHashed) {
        // 1. Load Precomputed Longitudinal Metrics (cached lookup)
        StudentLongitudinalMetrics longitudinal = fetchCachedLongitudinalMetrics(studentIdHashed);
        
        // 2. Check for active live session (in-memory lookup, no DB hit)
        // Assumption: UI or context passes the active sessionId if known, or we query live service.
        // We will default to checking if the child has an active session identifier.
        // For scaffolding, we request active session matching the studentId root.
        SessionLiveMetrics liveMetrics = liveSessionService.getLiveMetrics(studentIdHashed + "-active");

        return HybridClinicalDashboardDto.builder()
                .studentId(studentIdHashed)
                .longitudinalMetrics(longitudinal)
                .liveMetrics(liveMetrics.getEmotionalState() != null ? liveMetrics : null) // null if no active session tracking
                .build();
    }

    @Cacheable(value = "tier2Longitudinal", key = "#studentIdHashed")
    public StudentLongitudinalMetrics fetchCachedLongitudinalMetrics(String studentIdHashed) {
        log.info("Cache miss for {}, fetching longitudinal DB metrics...", studentIdHashed);
        return longitudinalMetricsRepository.findById(studentIdHashed)
                .orElseGet(() -> StudentLongitudinalMetrics.builder()
                        .studentId(studentIdHashed)
                        // Fallback defaults if aggregation hasn't run yet
                        .rollingVolatility7(0.0)
                        .rollingVolatility14(0.0)
                        .recoveryTrend(0.0)
                        .masteryVelocity(0.0)
                        .independenceScore(0.0)
                        .interventionDecayIndex(0.0)
                        .frustrationRiskScore(0.0)
                        .confidenceBandLow(0.0)
                        .confidenceBandHigh(0.0)
                        .lastUpdated(LocalDateTime.now())
                        .build());
    }
    @Cacheable(value = "tier2Dashboard", key = "#studentIdHashed")
    public Tier2FullDashboardDto generateClinicalSpecDashboard(String studentIdHashed) {
        log.info("Generating full Tier 2 dashboard payload for child {}", studentIdHashed);
        
        // --- 1. ZPD & Learning Stability
        Tier2FullDashboardDto.ZpdStabilityDto zpdStability = Tier2FullDashboardDto.ZpdStabilityDto.builder()
                .zpdElasticityScore(88.5)
                .timeInOptimalZonePercentage(65.0)
                .overshootEventsCount(4)
                .undershootEventsCount(12)
                .stabilityCurve(List.of(0.4, 0.5, 0.6, 0.8, 0.7))
                .driftDetectionAlert(false)
                .build();

        // --- 2. Emotional Regulation Analytics
        Tier2FullDashboardDto.EmotionalRegulationDto emotionalRegulation = Tier2FullDashboardDto.EmotionalRegulationDto.builder()
                .volatilityIndex(4.2)
                .recoveryLatencySeconds(45.5)
                .frustrationSpikeCount(3)
                .spikeDensityPerMinute(0.12)
                .valenceTrendCurve(List.of(-0.2, 0.1, 0.4, 0.5))
                .arousalTrendCurve(List.of(0.8, 0.6, 0.4, 0.3))
                .emotionalHeatmap(List.of(
                        Tier2FullDashboardDto.EmotionalRegulationDto.HeatmapPoint.builder().time("10:00").intensity(0.8).build(),
                        Tier2FullDashboardDto.EmotionalRegulationDto.HeatmapPoint.builder().time("10:15").intensity(0.2).build()
                ))
                .build();

        // --- 3. Longitudinal Emotional Trends
        Tier2FullDashboardDto.LongitudinalEmotionsDto longitudinalEmotions = Tier2FullDashboardDto.LongitudinalEmotionsDto.builder()
                .sevenSessionRollingVolatility(3.8)
                .fourteenSessionStabilityTrend(4.1)
                .recoveryTimeImprovementCurve(List.of(60.0, 55.0, 50.0, 45.5))
                .baselineShiftDetected(true)
                .escalationFrequencyTrend(List.of(5, 4, 3, 3, 2))
                .build();

        // --- 4. Predictive Risk Engine
        Tier2FullDashboardDto.PredictiveRiskEngineDto predictiveRiskEngine = Tier2FullDashboardDto.PredictiveRiskEngineDto.builder()
                .frustrationEscalationRiskPct(15.0)
                .masteryStagnationProbPct(22.5)
                .independenceTrajectoryProjection(List.of(60.0, 65.0, 70.0, 75.0))
                .overScaffoldingRiskIndex(0.35)
                .confidenceBand(Tier2FullDashboardDto.PredictiveRiskEngineDto.ConfidenceBand.builder()
                        .lowerBound(List.of(55.0, 60.0, 65.0, 70.0))
                        .upperBound(List.of(65.0, 70.0, 75.0, 80.0))
                        .build())
                .build();

        // --- 5. Intervention Intelligence
        Tier2FullDashboardDto.InterventionIntelligenceDto interventionIntelligence = Tier2FullDashboardDto.InterventionIntelligenceDto.builder()
                .successRatePerTool(List.of(
                        Tier2FullDashboardDto.InterventionIntelligenceDto.ToolSuccess.builder().toolName("Deep Breathing").successRate(85.0).build(),
                        Tier2FullDashboardDto.InterventionIntelligenceDto.ToolSuccess.builder().toolName("Visual Timer").successRate(60.0).build()
                ))
                .toolEffectivenessOverTime(List.of(0.9, 0.85, 0.8, 0.82))
                .habituationDecaySlope(-0.02)
                .interventionFrequencyTrend(List.of(10, 8, 7, 5))
                .dependencyRiskScore(0.2)
                .interventionTimingEfficiency(0.88)
                .build();

        // --- 6. Concept Mastery Deep View
        Tier2FullDashboardDto.ConceptMasteryDeepDto conceptMasteryDeep = Tier2FullDashboardDto.ConceptMasteryDeepDto.builder()
                .masteryLevelPerConcept(List.of(
                        Tier2FullDashboardDto.ConceptMasteryDeepDto.ConceptMastery.builder().concept("Addition").level(4.5).build(),
                        Tier2FullDashboardDto.ConceptMasteryDeepDto.ConceptMastery.builder().concept("Subtraction").level(3.2).build()
                ))
                .attemptsVsMasteryScatter(List.of(
                        Tier2FullDashboardDto.ConceptMasteryDeepDto.ScatterPoint.builder().concept("Addition").attempts(12).masteryLevel(4.5).build(),
                        Tier2FullDashboardDto.ConceptMasteryDeepDto.ScatterPoint.builder().concept("Subtraction").attempts(20).masteryLevel(3.2).build()
                ))
                .advancementVelocity(1.2)
                .difficultyProgressionCurve(List.of(1.0, 2.0, 2.5, 3.2))
                .timeToMasteryPerConcept(List.of(
                        Tier2FullDashboardDto.ConceptMasteryDeepDto.TimeMastery.builder().concept("Addition").hoursToMaster(4.5).build()
                ))
                .conceptRegressionDetection(List.of("Number Bonds"))
                .build();

        // --- 7. Independence & Scaffolding Analysis
        Tier2FullDashboardDto.IndependenceAnalysisDto independenceAnalysis = Tier2FullDashboardDto.IndependenceAnalysisDto.builder()
                .independentResponseRatio(0.68)
                .assistanceFrequency(0.32)
                .promptDependencyIndex(0.4)
                .autonomousCompletionTrend(List.of(0.5, 0.55, 0.6, 0.68))
                .growthInSelfRegulation(0.15)
                .build();

        // --- 8. Longitudinal Learning Intelligence
        Tier2FullDashboardDto.LongitudinalLearningDto longitudinalLearning = Tier2FullDashboardDto.LongitudinalLearningDto.builder()
                .rollingMasteryVelocity(1.1)
                .conceptRetentionStability(0.92)
                .crossConceptInterferenceDetected(false)
                .plateauDetection(true)
                .accelerationDecelerationPhases(List.of(
                        Tier2FullDashboardDto.LongitudinalLearningDto.Phase.ACCELERATION,
                        Tier2FullDashboardDto.LongitudinalLearningDto.Phase.PLATEAU
                ))
                .build();

        // --- 9. Timeline Explorer
        Tier2FullDashboardDto.TimelineExplorerDto timelineExplorer = Tier2FullDashboardDto.TimelineExplorerDto.builder()
                .scrubbableSessionTimeline(List.of(
                        Tier2FullDashboardDto.TimelineExplorerDto.TimelineEvent.builder()
                                .sessionTime("10:05").type(Tier2FullDashboardDto.TimelineExplorerDto.TimelineEvent.EventType.FRUSTRATION_SPIKE)
                                .description("Rapid task failure caused spike").build(),
                        Tier2FullDashboardDto.TimelineExplorerDto.TimelineEvent.builder()
                                .sessionTime("10:06").type(Tier2FullDashboardDto.TimelineExplorerDto.TimelineEvent.EventType.INTERVENTION_TRIGGER)
                                .description("System deployed deep breathing tool").build(),
                        Tier2FullDashboardDto.TimelineExplorerDto.TimelineEvent.builder()
                                .sessionTime("10:20").type(Tier2FullDashboardDto.TimelineExplorerDto.TimelineEvent.EventType.CONCEPT_MASTERY)
                                .description("Mastered addition with carryover").build()
                ))
                .build();

        // Return the compiled mega-payload
        return Tier2FullDashboardDto.builder()
                .studentIdHashed(studentIdHashed)
                .zpdStability(zpdStability)
                .emotionalRegulation(emotionalRegulation)
                .longitudinalEmotions(longitudinalEmotions)
                .predictiveRiskEngine(predictiveRiskEngine)
                .interventionIntelligence(interventionIntelligence)
                .conceptMasteryDeep(conceptMasteryDeep)
                .independenceAnalysis(independenceAnalysis)
                .longitudinalLearning(longitudinalLearning)
                .timelineExplorer(timelineExplorer)
                .build();
    }
}
