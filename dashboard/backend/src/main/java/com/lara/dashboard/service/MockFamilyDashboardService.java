package com.lara.dashboard.service;

import com.lara.dashboard.dto.FamilyDashboardResponse;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.repository.ChildRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Random;

/**
 * MockFamilyDashboardService
 *
 * Returns hardcoded structured analytics data for the Family Dashboard.
 * Data is deterministically generated based on childId.
 */
@Service
@RequiredArgsConstructor
public class MockFamilyDashboardService {

    private final ChildRepository childRepository;

    public FamilyDashboardResponse getDashboardData(String userEmail, Long childId) {
        Random random = new Random(childId == null ? 1 : childId);
        
        Child child = null;
        if (childId != null) {
             child = childRepository.findById(childId).orElse(null);
        }

        return FamilyDashboardResponse.builder()
                .childProfile(buildChildProfile(child, random))
                .sessionSummary(buildSessionSummary(random))
                .emotionalMetrics(buildEmotionalMetrics(random))
                .engagementMetrics(buildEngagementMetrics(random))
                .build();
    }

    private Map<String, Object> buildChildProfile(Child child, Random random) {
        Map<String, Object> profile = new HashMap<>();
        if (child != null) {
            profile.put("name", child.getName());
            profile.put("age", child.getAge());
            profile.put("gradeLevel", child.getGradeLevel());
            profile.put("therapistAssigned", child.getClinician() != null ? child.getClinician().getName() : "None Assigned");
        } else {
            profile.put("name", "Unknown Child");
            profile.put("age", 0);
            profile.put("gradeLevel", "N/A");
            profile.put("therapistAssigned", "None Assigned");
        }
        
        String[] focuses = {"Reading Comprehension", "Math Basics", "Social Scenarios", "Vocabulary"};
        String[] badges = {"Doing Well", "Improving", "Super Star", "Needs Encouragement"};
        
        profile.put("currentFocus", focuses[random.nextInt(focuses.length)]);
        profile.put("lastSessionTime", "Today, 2:30 PM"); // Mock
        profile.put("statusBadge", badges[random.nextInt(badges.length)]);
        return profile;
    }

    private Map<String, Object> buildSessionSummary(Random random) {
        Map<String, Object> session = new HashMap<>();
        session.put("totalSessionsThisWeek", 2 + random.nextInt(4));
        session.put("totalSessionsAllTime", 10 + random.nextInt(50));
        session.put("todaySessionDuration", (20 + random.nextInt(20)) + " minutes");
        session.put("averageSessionDuration", (20 + random.nextInt(15)) + " minutes");
        
        String[] activities = {"Story Sequencing", "Vocabulary Builder", "Pattern Matching", "Number Games"};
        session.put("lastActivityCompleted", activities[random.nextInt(activities.length)]);
        session.put("nextScheduledSession", "Tomorrow, 3:00 PM");
        session.put("weeklyGoalProgress", 40 + random.nextInt(60));
        session.put("activitiesCompletedToday", 1 + random.nextInt(4));

        String[] moods = {"Happy", "Calm", "Focused", "Engaged"};
        Map<String, Object> recentSessions = new HashMap<>();
        recentSessions.put("Monday", Map.of("duration", (20+random.nextInt(15))+" min", "mood", moods[random.nextInt(moods.length)], "score", 80+random.nextInt(20)));
        recentSessions.put("Tuesday", Map.of("duration", (20+random.nextInt(15))+" min", "mood", moods[random.nextInt(moods.length)], "score", 80+random.nextInt(20)));
        recentSessions.put("Wednesday", Map.of("duration", (20+random.nextInt(15))+" min", "mood", moods[random.nextInt(moods.length)], "score", 80+random.nextInt(20)));
        recentSessions.put("Thursday", Map.of("duration", (20+random.nextInt(15))+" min", "mood", moods[random.nextInt(moods.length)], "score", 80+random.nextInt(20)));
        session.put("recentSessions", recentSessions);

        return session;
    }

    private Map<String, Object> buildEmotionalMetrics(Random random) {
        Map<String, Object> emotional = new HashMap<>();
        int moodScore = 60 + random.nextInt(40);
        emotional.put("overallMoodScore", moodScore);
        
        String trend = moodScore > 85 ? "Improving" : moodScore < 70 ? "Needs Support" : "Stable";
        emotional.put("moodTrend", trend);
        
        String[] primaryEmotions = {"Calm", "Happy", "Focused", "Anxious"};
        emotional.put("primaryEmotion", primaryEmotions[random.nextInt(primaryEmotions.length)]);
        emotional.put("emotionStability", 60 + random.nextInt(40));
        
        String anxiety = random.nextInt(100) > 80 ? "Medium" : "Low";
        emotional.put("anxietyLevel", anxiety);
        emotional.put("selfRegulationScore", 60 + random.nextInt(40));
        emotional.put("positiveInteractions", 5 + random.nextInt(15));
        emotional.put("challengingMoments", random.nextInt(5));

        emotional.put("weeklyMoodData", List.of(
                Map.of("day", "Mon", "score", 60+random.nextInt(40)),
                Map.of("day", "Tue", "score", 60+random.nextInt(40)),
                Map.of("day", "Wed", "score", 60+random.nextInt(40)),
                Map.of("day", "Thu", "score", 60+random.nextInt(40)),
                Map.of("day", "Fri", "score", 60+random.nextInt(40))
        ));

        int happy = 20 + random.nextInt(30);
        int calm = 20 + random.nextInt(30);
        int focused = 15 + random.nextInt(25);
        int anxious = random.nextInt(15);
        int frustrated = 100 - (happy + calm + focused + anxious);
        if (frustrated < 0) frustrated = 0; // fallback safety
        
        emotional.put("emotionBreakdown", Map.of(
                "Happy", happy,
                "Calm", calm,
                "Focused", focused,
                "Anxious", anxious,
                "Frustrated", frustrated
        ));

        return emotional;
    }

    private Map<String, Object> buildEngagementMetrics(Random random) {
        Map<String, Object> engagement = new HashMap<>();
        engagement.put("focusScore", 65 + random.nextInt(35));
        engagement.put("attentionSpanMinutes", 15 + random.nextInt(15));
        engagement.put("taskCompletionRate", 70 + random.nextInt(30));
        
        String participation = random.nextInt(100) > 80 ? "Medium" : "High";
        engagement.put("participationLevel", participation);
        engagement.put("distractionFrequency", "Low");
        engagement.put("responsiveness", 70 + random.nextInt(30));
        engagement.put("initiativeTaking", 50 + random.nextInt(50));
        engagement.put("collaborationScore", 60 + random.nextInt(40));

        engagement.put("weeklyFocusData", List.of(
                Map.of("day", "Mon", "focus", 65+random.nextInt(35), "attention", 15+random.nextInt(15)),
                Map.of("day", "Tue", "focus", 65+random.nextInt(35), "attention", 15+random.nextInt(15)),
                Map.of("day", "Wed", "focus", 65+random.nextInt(35), "attention", 15+random.nextInt(15)),
                Map.of("day", "Thu", "focus", 65+random.nextInt(35), "attention", 15+random.nextInt(15)),
                Map.of("day", "Fri", "focus", 65+random.nextInt(35), "attention", 15+random.nextInt(15))
        ));

        engagement.put("topActivities", List.of(
                Map.of("name", "Story Sequencing", "score", 70+random.nextInt(30), "completions", 2+random.nextInt(10)),
                Map.of("name", "Vocabulary Builder", "score", 70+random.nextInt(30), "completions", 2+random.nextInt(10)),
                Map.of("name", "Reading Comprehension", "score", 70+random.nextInt(30), "completions", 2+random.nextInt(10)),
                Map.of("name", "Social Scenarios", "score", 70+random.nextInt(30), "completions", 2+random.nextInt(10))
        ));

        return engagement;
    }
}
