package com.lara.dashboard.service;

import com.lara.dashboard.dto.FamilyDashboardResponse;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.EmotionalMetric;
import com.lara.dashboard.entity.Session;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.EmotionalMetricRepository;
import com.lara.dashboard.repository.SessionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FamilyDashboardService {

    private final ChildRepository childRepository;
    private final SessionRepository sessionRepository;
    private final EmotionalMetricRepository emotionalMetricRepository;

    public FamilyDashboardResponse getDashboardData(String userEmail, Long childId) {
        if (childId == null) {
            return FamilyDashboardResponse.builder().build();
        }

        Child child = childRepository.findById(childId)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        List<Session> sessions = sessionRepository.findAllByChild_Id(childId);
        String childHash = String.valueOf(childId); // Assuming childId is used as hash for metrics in this context

        return FamilyDashboardResponse.builder()
                .childProfile(buildChildProfile(child, sessions))
                .sessionSummary(buildSessionSummary(sessions))
                .emotionalMetrics(buildEmotionalMetrics(childHash))
                .engagementMetrics(buildEngagementMetrics(sessions))
                .build();
    }

    private Map<String, Object> buildChildProfile(Child child, List<Session> sessions) {
        Map<String, Object> profile = new HashMap<>();
        profile.put("name", child.getName());
        profile.put("age", child.getAge());
        profile.put("gradeLevel", child.getGradeLevel());
        profile.put("therapistAssigned", child.getClinician() != null ? child.getClinician().getName() : "None Assigned");
        
        Session lastSession = sessions.stream()
                .max(Comparator.comparing(Session::getStartTime))
                .orElse(null);

        profile.put("lastSessionTime", lastSession != null && lastSession.getStartTime() != null ? 
                lastSession.getStartTime().format(DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm")) : "No sessions yet");
        
        profile.put("currentFocus", "Social Skills"); // Keep mock for now
        profile.put("statusBadge", "Steady Progress"); // Keep mock
        
        return profile;
    }

    private Map<String, Object> buildSessionSummary(List<Session> sessions) {
        LocalDateTime weekAgo = LocalDateTime.now().minusDays(7);
        List<Session> thisWeek = sessions.stream()
                .filter(s -> s.getStartTime() != null && s.getStartTime().isAfter(weekAgo))
                .collect(Collectors.toList());

        Map<String, Object> summary = new HashMap<>();
        summary.put("totalSessionsThisWeek", thisWeek.size());
        summary.put("totalSessionsAllTime", sessions.size());
        
        long todaySeconds = sessions.stream()
                .filter(s -> s.getStartTime() != null && s.getStartTime().toLocalDate().equals(LocalDateTime.now().toLocalDate()))
                .mapToLong(s -> s.getDurationSeconds() != null ? s.getDurationSeconds() : 0)
                .sum();
        
        summary.put("todaySessionDuration", (todaySeconds / 60) + " minutes");
        summary.put("activitiesCompletedToday", (int) sessions.stream()
                .filter(s -> s.getStartTime() != null && s.getStartTime().toLocalDate().equals(LocalDateTime.now().toLocalDate()))
                .count());

        summary.put("weeklyGoalProgress", Math.min(100, (thisWeek.size() * 100 / 5))); // Goal 5 sessions/week
        return summary;
    }

    private Map<String, Object> buildEmotionalMetrics(String childHash) {
        LocalDateTime monthAgo = LocalDateTime.now().minusDays(30);
        List<EmotionalMetric> metrics = emotionalMetricRepository.findByChildIdHashedAndTimestampAfter(childHash, monthAgo);

        Map<String, Object> emotional = new HashMap<>();
        double avgMood = metrics.stream().mapToInt(EmotionalMetric::getMoodScore).average().orElse(0.0);
        emotional.put("overallMoodScore", (int) avgMood);
        
        Map<String, Long> counts = metrics.stream()
                .collect(Collectors.groupingBy(EmotionalMetric::getPrimaryEmotion, Collectors.counting()));
        
        String primary = counts.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse("Neutral");
        
        emotional.put("primaryEmotion", primary);
        
        long total = metrics.size();
        Map<String, Integer> breakdown = new HashMap<>();
        if (total > 0) {
            counts.forEach((k, v) -> breakdown.put(k, (int)(v * 100 / total)));
        }
        emotional.put("emotionBreakdown", breakdown);
        emotional.put("moodTrend", avgMood > 80 ? "Improving" : "Stable");
        emotional.put("emotionStability", 85); // Placeholder
        return emotional;
    }

    private Map<String, Object> buildEngagementMetrics(List<Session> sessions) {
        Map<String, Object> engagement = new HashMap<>();
        double avgFocus = sessions.stream()
                .filter(s -> s.getAvgMoodConfidence() != null)
                .mapToDouble(Session::getAvgMoodConfidence)
                .average().orElse(0.0) * 100;

        engagement.put("focusScore", (int) avgFocus);
        engagement.put("participationLevel", avgFocus > 70 ? "High" : "Medium");
        engagement.put("taskCompletionRate", 90);
        return engagement;
    }
}
