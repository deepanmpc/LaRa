package com.lara.dashboard.controller;

import com.lara.dashboard.dto.SimpleAnalyticsDto;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/analytics/simple")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173")
public class SimpleAnalyticsController {

    @GetMapping("/{studentIdHashed}")
    public ResponseEntity<SimpleAnalyticsDto> getSimpleAnalytics(@PathVariable String studentIdHashed) {
        // Mocking the translation of complex backend metrics to simple English logic
        // This is where EWMA, Decay Slopes, and ZPD Data normally get parsed.
        
        SimpleAnalyticsDto dto = SimpleAnalyticsDto.builder()
                .sessionSummary(SimpleAnalyticsDto.SessionSummary.builder()
                        .learningFocus("Fractions & Division")
                        .emotionalStabilityStatus("Stable") // Mapped from ZPD Elasticity
                        .conceptsPracticed(List.of("Intro to Fractions", "Basic Geometry"))
                        .conceptsMastered(List.of("Intro to Fractions"))
                        .recommendedNextSteps("Continue practicing basic division to reinforce fraction concepts.")
                        .build())
                .emotionalOverview(SimpleAnalyticsDto.EmotionalOverview.builder()
                        .recoverySpeed("Fast") // Mapped from Latency < 15s
                        .frustrationSpikes(1)
                        .weekOverWeekTrend("Improved")
                        .build())
                .interventionSummary(SimpleAnalyticsDto.InterventionSummary.builder()
                        .primaryToolEffectiveness("Breathing exercises helped 2 out of 2 times.") // Mapped from > 75% Overall Success
                        .secondaryToolEffectiveness("Gentle nudges were effective.")
                        .generalRecommendation("The current coping strategies are working beautifully.")
                        .build())
                .progressSnapshot(List.of(
                        SimpleAnalyticsDto.ConceptProgress.builder().conceptName("Intro to Fractions").masteryPercentage(85).trend("UP").build(),
                        SimpleAnalyticsDto.ConceptProgress.builder().conceptName("Basic Geometry").masteryPercentage(45).trend("STABLE").build(),
                        SimpleAnalyticsDto.ConceptProgress.builder().conceptName("Word Problems").masteryPercentage(20).trend("DOWN").build()
                ))
                .build();

        return ResponseEntity.ok(dto);
    }
}
