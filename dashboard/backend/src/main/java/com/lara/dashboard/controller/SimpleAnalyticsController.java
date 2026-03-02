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
        // Mocking the extraction of complex backend metrics (Latency, Volatility, Regression Decay)
        // transposing them down into plain-English DTOs avoiding all statistical jargon.
        
        SimpleAnalyticsDto dto = SimpleAnalyticsDto.builder()
                .activeChildOverview(SimpleAnalyticsDto.ActiveChildOverview.builder()
                        .childName("Leo Smith")
                        .age(6)
                        .currentLearningTheme("Fractions & Shapes")
                        .lastSessionDate("Today, 2:30 PM")
                        .overallStatusBadge("Doing Well") // Mapped from positive ZPD + low Frustration
                        .build())

                .sessionSummary(SimpleAnalyticsDto.SessionSummary.builder()
                        .learningFocus("Fractions & Division")
                        .emotionalStabilityStatus("Stable") 
                        .conceptsPracticed(List.of("Intro to Fractions", "Basic Geometry"))
                        .conceptsMastered(List.of("Intro to Fractions"))
                        .aiNarrativeSummary("Leo had a wonderful session today. He grasped the concept of basic fractions very quickly and remained completely engaged. When things got slightly tricky during division, he took a deep breath on his own and powered through. No intervention was needed!")
                        .build())

                .weeklySnapshot(SimpleAnalyticsDto.WeeklySnapshot.builder()
                        .sessionsCompleted(4)
                        .totalLearningTime("2h 15m")
                        .conceptsAdvanced(3)
                        .emotionalStabilityTrend("Improving")
                        .weeklySummarySentence("This week showed steady progress with highly improved emotional regulation compared to last week.")
                        .build())

                .emotionalOverview(SimpleAnalyticsDto.EmotionalOverview.builder()
                        .recoverySpeed("Fast") // Mapped from Latency < 15s
                        .frustrationSpikes(1)
                        .weekOverWeekTrend("Improved")
                        .build())

                .engagementIndicator(SimpleAnalyticsDto.EngagementIndicator.builder()
                        .engagementLevel("Highly Engaged") // Mapped from Vision Tracking thresholds
                        .participationScore("Active")      // Mapped from speech frequency
                        .build())

                .interventionSummary(SimpleAnalyticsDto.InterventionSummary.builder()
                        .effectivenessStatements(List.of(
                                "Breathing exercises helped 2 out of 2 times.",
                                "Gentle nudges were very effective today."
                        ))
                        .generalRecommendation("The current coping strategies are working beautifully. Consider continuing them next week.")
                        .build())

                .milestonesAndAchievements(List.of(
                        "🎉 Completed first independent counting sequence.",
                        "🌟 Managed a moment of frustration without any robot assistance!",
                        "🏆 Improved recovery time by 30% compared to last week."
                ))

                .recommendedNextSteps(List.of(
                        "Continue practicing division to reinforce the fraction concepts.",
                        "Offer brief breaks if the geometry sections begin to feel long.",
                        "Try a new storytelling activity to mix up the math routines."
                ))

                .progressSnapshot(List.of(
                        SimpleAnalyticsDto.ConceptProgress.builder().conceptName("Intro to Fractions").masteryPercentage(85).trend("UP").build(),
                        SimpleAnalyticsDto.ConceptProgress.builder().conceptName("Basic Geometry").masteryPercentage(45).trend("STABLE").build(),
                        SimpleAnalyticsDto.ConceptProgress.builder().conceptName("Word Problems").masteryPercentage(20).trend("DOWN").build()
                ))

                .sessionHistory(List.of(
                        SimpleAnalyticsDto.SessionHistoryCard.builder().date("Oct 24").duration("30m").emotionalSummary("Stable and happy").progressIndicator("Strong Progress").build(),
                        SimpleAnalyticsDto.SessionHistoryCard.builder().date("Oct 22").duration("25m").emotionalSummary("Slightly challenged, but recovered").progressIndicator("Developing").build(),
                        SimpleAnalyticsDto.SessionHistoryCard.builder().date("Oct 20").duration("40m").emotionalSummary("Highly engaged").progressIndicator("Strong Progress").build()
                ))

                .build();

        return ResponseEntity.ok(dto);
    }

    @PostMapping("/{studentIdHashed}/notes")
    public ResponseEntity<String> saveCaregiverNotes(@PathVariable String studentIdHashed, @RequestBody CaregiverNoteRequest request) {
        // In a real application, this would save to a CaregiverNote entity linked to the student
        System.out.println("Saved caregiver note for " + studentIdHashed + ": " + request.note());
        return ResponseEntity.ok("Note saved successfully.");
    }

    record CaregiverNoteRequest(String note) {}
}
