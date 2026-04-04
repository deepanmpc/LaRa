package com.lara.dashboard.service;

import com.lara.dashboard.dto.ChildProfileDTO;
import com.lara.dashboard.dto.EmotionalSummaryDTO;
import com.lara.dashboard.dto.EngagementSummaryDTO;
import com.lara.dashboard.dto.FamilyDashboardResponse;
import com.lara.dashboard.dto.SessionSummaryDTO;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.Session;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.SessionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
public class FamilyDashboardService {

    private final ChildRepository childRepository;
    private final SessionRepository sessionRepository;

    public FamilyDashboardResponse getDashboardData(String userEmail, Long childId) {
        Child child = null;
        if (childId != null) {
             child = childRepository.findById(childId).orElse(null);
        }

        List<Session> allSessions = childId != null ? sessionRepository.findAllByChild_Id(childId) : List.of();

        return FamilyDashboardResponse.builder()
                .childProfile(buildChildProfile(child))
                .sessionSummary(buildSessionSummary(allSessions))
                .emotionalMetrics(buildEmotionalMetrics(allSessions))
                .engagementMetrics(buildEngagementMetrics(allSessions))
                .build();
    }

    private ChildProfileDTO buildChildProfile(Child child) {
        String name = "Unknown Child";
        Integer age = 0;
        String gradeLevel = "N/A";
        String therapistAssigned = "None Assigned";
        
        if (child != null) {
            name = child.getName();
            age = child.getAge();
            gradeLevel = child.getGradeLevel();
            therapistAssigned = child.getClinician() != null ? child.getClinician().getUser().getName() : "None Assigned";
        }
        
        return ChildProfileDTO.builder()
            .name(name)
            .age(age)
            .gradeLevel(gradeLevel)
            .therapistAssigned(therapistAssigned)
            .currentFocus("Social Scenarios")
            .lastSessionTime("Recently")
            .statusBadge("Doing Well")
            .build();
    }

    private SessionSummaryDTO buildSessionSummary(List<Session> sessions) {
        long recentSessionsCount = sessions.stream()
                .filter(s -> s.getStartTime() != null && s.getStartTime().isAfter(LocalDateTime.now().minusDays(7)))
                .count();

        int totalMins = sessions.stream()
                .mapToInt(s -> s.getDurationSeconds() != null ? s.getDurationSeconds() : 0)
                .sum() / 60;

        int avgMins = sessions.isEmpty() ? 0 : totalMins / sessions.size();

        return SessionSummaryDTO.builder()
            .totalSessionsThisWeek(recentSessionsCount)
            .totalSessionsAllTime(sessions.size())
            .todaySessionDuration((sessions.isEmpty() ? 0 : sessions.get(sessions.size()-1).getDurationSeconds() != null ? sessions.get(sessions.size()-1).getDurationSeconds() / 60 : 0) + " minutes")
            .averageSessionDuration(avgMins + " minutes")
            .lastActivityCompleted(sessions.isEmpty() ? "None" : sessions.get(sessions.size()-1).getInterventionUsed())
            .nextScheduledSession("Configure via Calendar")
            .weeklyGoalProgress((int)Math.min(100, recentSessionsCount * 25))
            .activitiesCompletedToday(1)
            .recentSessions(new HashMap<>())
            .build();
    }

    private EmotionalSummaryDTO buildEmotionalMetrics(List<Session> sessions) {
        double avgScore = sessions.stream()
            .mapToDouble(s -> s.getAvgMoodConfidence() != null ? s.getAvgMoodConfidence() : 80.0)
            .average().orElse(80.0);

        String trend = avgScore > 85 ? "Improving" : avgScore < 70 ? "Needs Support" : "Stable";
        
        return EmotionalSummaryDTO.builder()
            .overallMoodScore((int)avgScore)
            .moodTrend(trend)
            .primaryEmotion("Calm")
            .emotionStability((int)avgScore)
            .anxietyLevel("Low")
            .selfRegulationScore((int)avgScore - 5)
            .positiveInteractions(sessions.size() * 2)
            .challengingMoments(sessions.stream().mapToInt(s -> s.getTotalInterventions() != null ? s.getTotalInterventions() : 0).sum())
            .weeklyMoodData(List.of(
                Map.of("day", "Mon", "score", (int)avgScore),
                Map.of("day", "Tue", "score", (int)avgScore)
            ))
            .emotionBreakdown(Map.of(
                "Happy", 40,
                "Calm", 40,
                "Focused", 10,
                "Anxious", 5,
                "Frustrated", 5
            ))
            .build();
    }

    private EngagementSummaryDTO buildEngagementMetrics(List<Session> sessions) {
        int focus = sessions.isEmpty() ? 75 : 85;

        return EngagementSummaryDTO.builder()
            .focusScore(focus)
            .attentionSpanMinutes(15)
            .taskCompletionRate(80)
            .participationLevel("High")
            .distractionFrequency("Low")
            .responsiveness(focus)
            .initiativeTaking(focus - 10)
            .collaborationScore(focus - 5)
            .weeklyFocusData(List.of(
                Map.of("day", "Mon", "focus", focus, "attention", 15),
                Map.of("day", "Tue", "focus", focus, "attention", 15)
            ))
            .topActivities(List.of(
                Map.of("name", "Standard Interaction", "score", focus, "completions", sessions.size())
            ))
            .build();
    }
}
