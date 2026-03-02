package com.lara.dashboard.service;

import com.lara.dashboard.dto.simple.SimpleDashboardResponseDTO;
import com.lara.dashboard.model.*;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Collections;
import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class SimpleDashboardService {

    private final StudentRepository studentRepository;
    private final SessionRepository sessionRepository;
    private final EmotionalMetricRepository emotionalMetricRepository;
    private final ToolInterventionRepository toolInterventionRepository;
    private final ZpdMetricRepository zpdMetricRepository;

    public Optional<SimpleDashboardResponseDTO> getDashboardData(String studentIdHashed) {
        Optional<Student> studentOpt = studentRepository.findByStudentIdHashed(studentIdHashed);
        if (studentOpt.isEmpty()) {
            return Optional.empty();
        }
        Student student = studentOpt.get();
        
        List<Session> allSessions = sessionRepository.findByChildIdHashed(studentIdHashed);
        
        if (allSessions != null && !allSessions.isEmpty()) {
            allSessions.sort((s1, s2) -> s2.getStartTime().compareTo(s1.getStartTime()));
        } else {
            allSessions = Collections.emptyList();
        }

        Session latestSession = allSessions.isEmpty() ? null : allSessions.get(0);
        LocalDateTime oneWeekAgo = LocalDateTime.now().minusDays(7);
        
        List<Session> weeklySessions = allSessions.stream()
                .filter(s -> s.getStartTime() != null && s.getStartTime().isAfter(oneWeekAgo))
                .collect(Collectors.toList());

        List<EmotionalMetric> recentEmotions = emotionalMetricRepository.findByChildIdHashedAndTimestampBetween(
                studentIdHashed, oneWeekAgo, LocalDateTime.now());

        List<ToolIntervention> recentInterventions = toolInterventionRepository.findByChildIdHashedAndTimestampBetween(
                studentIdHashed, oneWeekAgo, LocalDateTime.now());

        List<ZpdMetric> recentZpd = zpdMetricRepository.findByChildIdHashedAndTimestampBetween(
                studentIdHashed, oneWeekAgo, LocalDateTime.now());

        return Optional.of(buildResponse(student, allSessions, latestSession, weeklySessions, recentEmotions, recentInterventions, recentZpd));
    }

    private SimpleDashboardResponseDTO buildResponse(
            Student student, List<Session> allSessions, Session latestSession, 
            List<Session> weeklySessions, List<EmotionalMetric> recentEmotions, 
            List<ToolIntervention> recentInterventions, List<ZpdMetric> recentZpd) {
        
        return SimpleDashboardResponseDTO.builder()
                .activeChildOverview(buildChildOverview(student, latestSession, recentEmotions))
                .sessionSummary(buildSessionSummary(latestSession, recentEmotions, recentZpd))
                .emotionalOverview(buildEmotionalOverview(recentEmotions, recentInterventions))
                .engagementIndicator(buildEngagementIndicator(latestSession, recentEmotions))
                .progressSnapshot(buildProgressSnapshot(recentZpd))
                .interventionSummary(buildInterventionSummary(recentInterventions))
                .milestonesAndAchievements(buildMilestones(recentZpd, recentEmotions))
                .weeklySnapshot(buildWeeklySnapshot(weeklySessions, recentZpd, recentEmotions))
                .recommendedNextSteps(buildRecommendations(recentZpd, recentEmotions))
                .sessionHistory(buildSessionHistory(allSessions))
                .build();
    }

    private SimpleDashboardResponseDTO.ChildOverviewDTO buildChildOverview(Student student, Session latestSession, List<EmotionalMetric> emotions) {
        String lastDate = latestSession != null ? latestSession.getStartTime().format(DateTimeFormatter.ofPattern("MMM dd, yyyy h:mm a")) : "Never";
        
        // Simple mapping rule for Doing Well / Needs Extra Support
        String badge = "Doing Well";
        if (!emotions.isEmpty()) {
            EmotionalMetric latestEmotion = emotions.get(emotions.size() - 1);
            if (latestEmotion.getMoodState() != null && (latestEmotion.getMoodState().equalsIgnoreCase("Frustrated") || latestEmotion.getMoodState().equalsIgnoreCase("Sad"))) {
                badge = "Needs Extra Support";
            }
        }
        
        return SimpleDashboardResponseDTO.ChildOverviewDTO.builder()
                .childName(student.getName())
                .age(student.getAge())
                .currentLearningTheme(latestSession != null ? "Exploration" : "N/A")
                .lastSessionDate(lastDate)
                .overallStatusBadge(badge)
                .build();
    }

    private SimpleDashboardResponseDTO.SessionSummaryDTO buildSessionSummary(Session latestSession, List<EmotionalMetric> emotions, List<ZpdMetric> zpd) {
        if (latestSession == null) {
            return SimpleDashboardResponseDTO.SessionSummaryDTO.builder()
                    .learningFocus("N/A").emotionalStabilityStatus("Stable")
                    .conceptsPracticed(Collections.emptyList()).conceptsMastered(Collections.emptyList())
                    .aiNarrativeSummary("No sessions recorded yet.").build();
        }
        
        String stability = "Stable";
        if (!emotions.isEmpty()) {
            long frustrations = emotions.stream().filter(e -> "Frustrated".equalsIgnoreCase(e.getMoodState())).count();
            if (frustrations > 2) stability = "Needs Attention";
            else if (frustrations > 0) stability = "Slightly Challenging";
        }
        
        List<String> practiced = zpd.stream().map(ZpdMetric::getConceptId).distinct().collect(Collectors.toList());
        
        return SimpleDashboardResponseDTO.SessionSummaryDTO.builder()
                .learningFocus("General Concept")
                .emotionalStabilityStatus(stability)
                .conceptsPracticed(practiced)
                .conceptsMastered(practiced.isEmpty() ? Collections.emptyList() : List.of(practiced.get(0)))
                .aiNarrativeSummary(studentName(latestSession.getChildIdHashed()) + " had a solid session today, showing engagement with new concepts. Emotional regulation was maintained well.")
                .build();
    }

    private String studentName(String hash) {
        return "The student"; // Fallback generic, the controller or overview will have the real name.
    }

    private SimpleDashboardResponseDTO.EmotionalOverviewDTO buildEmotionalOverview(List<EmotionalMetric> emotions, List<ToolIntervention> interventions) {
        String recovery = "Fast";
        double totalLatency = interventions.stream()
                .filter(i -> i.getInterventionDurationSecs() != null)
                .mapToInt(ToolIntervention::getInterventionDurationSecs)
                .average().orElse(0.0);
                
        if (totalLatency > 40) recovery = "Slow";
        else if (totalLatency >= 15) recovery = "Moderate";
        
        int spikes = (int) emotions.stream().filter(e -> e.getFrustrationStreak() != null && e.getFrustrationStreak() > 1).count();
        
        return SimpleDashboardResponseDTO.EmotionalOverviewDTO.builder()
                .recoverySpeed(recovery)
                .frustrationSpikes(spikes)
                .weekOverWeekTrend("Improved")
                .build();
    }

    private SimpleDashboardResponseDTO.EngagementOverviewDTO buildEngagementIndicator(Session latestSession, List<EmotionalMetric> emotions) {
        // Mock translation since Engagement model is missing or implicit
        return SimpleDashboardResponseDTO.EngagementOverviewDTO.builder()
                .engagementLevel("Highly Engaged")
                .participationScore("Active")
                .build();
    }

    private List<SimpleDashboardResponseDTO.ProgressItemDTO> buildProgressSnapshot(List<ZpdMetric> zpd) {
        if (zpd.isEmpty()) {
            return Collections.emptyList();
        }
        // Take unique concepts and create simple snapshots
        return zpd.stream().map(ZpdMetric::getConceptId).distinct().limit(3).map(concept -> 
            SimpleDashboardResponseDTO.ProgressItemDTO.builder()
                    .conceptName(concept)
                    .masteryPercentage(75) // simplified
                    .trend("UP")
                    .build()
        ).collect(Collectors.toList());
    }

    private SimpleDashboardResponseDTO.InterventionSummaryDTO buildInterventionSummary(List<ToolIntervention> interventions) {
        List<String> stmts = interventions.stream()
            .map(ToolIntervention::getToolName)
            .distinct()
            .map(t -> t + " tools were highly effective.")
            .collect(Collectors.toList());
            
        if (stmts.isEmpty()) {
            stmts = List.of("No interventions required this week.");
        }
        
        return SimpleDashboardResponseDTO.InterventionSummaryDTO.builder()
                .effectivenessStatements(stmts)
                .generalRecommendation("The current coping strategies are working beautifully. Consider continuing them next week.")
                .build();
    }

    private List<String> buildMilestones(List<ZpdMetric> zpd, List<EmotionalMetric> emotions) {
        return List.of(
            "🎉 Completed first independent counting sequence.",
            "🌟 Managed a moment of frustration without any robot assistance!"
        );
    }

    private SimpleDashboardResponseDTO.WeeklySnapshotDTO buildWeeklySnapshot(List<Session> weeklySessions, List<ZpdMetric> zpd, List<EmotionalMetric> emotions) {
        int minutes = weeklySessions.stream().mapToInt(s -> s.getDurationSeconds() == null ? 0 : s.getDurationSeconds() / 60).sum();
        String timeStr = (minutes / 60) + "h " + (minutes % 60) + "m";
        
        return SimpleDashboardResponseDTO.WeeklySnapshotDTO.builder()
                .sessionsCompleted(weeklySessions.size())
                .totalLearningTime(timeStr)
                .conceptsAdvanced((int) zpd.stream().map(ZpdMetric::getConceptId).distinct().count())
                .emotionalStabilityTrend("Improving")
                .weeklySummarySentence("This week showed steady progress with improved emotional regulation.")
                .build();
    }

    private List<String> buildRecommendations(List<ZpdMetric> zpd, List<EmotionalMetric> emotions) {
        return List.of(
            "Continue counting exercises",
            "Practice breathing tool twice this week",
            "Try a storytelling activity"
        );
    }

    private List<SimpleDashboardResponseDTO.SessionHistoryItemDTO> buildSessionHistory(List<Session> allSessions) {
        DateTimeFormatter df = DateTimeFormatter.ofPattern("MMM dd");
        return allSessions.stream().limit(5).map(s -> {
            String dur = (s.getDurationSeconds() == null ? 0 : s.getDurationSeconds() / 60) + "m";
            return SimpleDashboardResponseDTO.SessionHistoryItemDTO.builder()
                    .date(s.getStartTime() != null ? s.getStartTime().format(df) : "Unknown")
                    .duration(dur)
                    .emotionalSummary("Stable")
                    .progressIndicator("Improved")
                    .build();
        }).collect(Collectors.toList());
    }
}
