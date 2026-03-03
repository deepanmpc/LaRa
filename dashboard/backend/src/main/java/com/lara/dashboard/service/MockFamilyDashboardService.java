package com.lara.dashboard.service;

import com.lara.dashboard.dto.FamilyDashboardResponse;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * MockFamilyDashboardService
 *
 * Returns hardcoded structured analytics data for the Family Dashboard.
 * NO model calls. NO AI execution.
 * 
 * Future: Replace with ModelAnalyticsService without redesigning architecture.
 */
@Service
public class MockFamilyDashboardService {

    public FamilyDashboardResponse getDashboardData(String userEmail) {
        return FamilyDashboardResponse.builder()
                .childProfile(buildChildProfile())
                .sessionSummary(buildSessionSummary())
                .emotionalMetrics(buildEmotionalMetrics())
                .engagementMetrics(buildEngagementMetrics())
                .build();
    }

    private Map<String, Object> buildChildProfile() {
        Map<String, Object> profile = new HashMap<>();
        profile.put("name", "Alex Johnson");
        profile.put("age", 9);
        profile.put("gradeLevel", "Grade 4");
        profile.put("currentFocus", "Reading Comprehension");
        profile.put("lastSessionTime", "Today, 2:30 PM");
        profile.put("statusBadge", "Doing Well");
        profile.put("therapistAssigned", "Dr. Sarah Mitchell");
        return profile;
    }

    private Map<String, Object> buildSessionSummary() {
        Map<String, Object> session = new HashMap<>();
        session.put("totalSessionsThisWeek", 4);
        session.put("totalSessionsAllTime", 47);
        session.put("todaySessionDuration", "32 minutes");
        session.put("averageSessionDuration", "28 minutes");
        session.put("lastActivityCompleted", "Story Sequencing");
        session.put("nextScheduledSession", "Tomorrow, 3:00 PM");
        session.put("weeklyGoalProgress", 80);
        session.put("activitiesCompletedToday", 3);

        Map<String, Object> recentSessions = new HashMap<>();
        recentSessions.put("Monday", Map.of("duration", "30 min", "mood", "Happy", "score", 88));
        recentSessions.put("Tuesday", Map.of("duration", "25 min", "mood", "Calm", "score", 92));
        recentSessions.put("Wednesday", Map.of("duration", "28 min", "mood", "Focused", "score", 85));
        recentSessions.put("Thursday", Map.of("duration", "32 min", "mood", "Engaged", "score", 90));
        session.put("recentSessions", recentSessions);

        return session;
    }

    private Map<String, Object> buildEmotionalMetrics() {
        Map<String, Object> emotional = new HashMap<>();
        emotional.put("overallMoodScore", 87);
        emotional.put("moodTrend", "Improving");
        emotional.put("primaryEmotion", "Calm");
        emotional.put("emotionStability", 82);
        emotional.put("anxietyLevel", "Low");
        emotional.put("selfRegulationScore", 78);
        emotional.put("positiveInteractions", 14);
        emotional.put("challengingMoments", 2);

        emotional.put("weeklyMoodData", List.of(
                Map.of("day", "Mon", "score", 80),
                Map.of("day", "Tue", "score", 85),
                Map.of("day", "Wed", "score", 83),
                Map.of("day", "Thu", "score", 90),
                Map.of("day", "Fri", "score", 87)
        ));

        emotional.put("emotionBreakdown", Map.of(
                "Happy", 45,
                "Calm", 30,
                "Focused", 15,
                "Anxious", 7,
                "Frustrated", 3
        ));

        return emotional;
    }

    private Map<String, Object> buildEngagementMetrics() {
        Map<String, Object> engagement = new HashMap<>();
        engagement.put("focusScore", 88);
        engagement.put("attentionSpanMinutes", 22);
        engagement.put("taskCompletionRate", 91);
        engagement.put("participationLevel", "High");
        engagement.put("distractionFrequency", "Low");
        engagement.put("responsiveness", 94);
        engagement.put("initiativeTaking", 72);
        engagement.put("collaborationScore", 85);

        engagement.put("weeklyFocusData", List.of(
                Map.of("day", "Mon", "focus", 82, "attention", 20),
                Map.of("day", "Tue", "focus", 90, "attention", 25),
                Map.of("day", "Wed", "focus", 85, "attention", 22),
                Map.of("day", "Thu", "focus", 92, "attention", 24),
                Map.of("day", "Fri", "focus", 88, "attention", 22)
        ));

        engagement.put("topActivities", List.of(
                Map.of("name", "Story Sequencing", "score", 95, "completions", 8),
                Map.of("name", "Vocabulary Builder", "score", 88, "completions", 12),
                Map.of("name", "Reading Comprehension", "score", 83, "completions", 6),
                Map.of("name", "Social Scenarios", "score", 79, "completions", 5)
        ));

        return engagement;
    }
}
