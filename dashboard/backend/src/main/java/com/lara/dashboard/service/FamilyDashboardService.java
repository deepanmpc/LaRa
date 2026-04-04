package com.lara.dashboard.service;

import com.lara.dashboard.dto.*;
import com.lara.dashboard.entity.*;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class FamilyDashboardService {

    private final ChildRepository childRepository;
    private final SessionRepository sessionRepository;
    private final SessionAnalyticsRepository analyticsRepository;
    private final ChildEmotionalHistoryRepository emotionalHistoryRepository;
    private final ChildEngagementHistoryRepository engagementHistoryRepository;
    private final ChildActivityPerformanceRepository activityPerformanceRepository;
    private final WeeklySessionSummaryRepository weeklySummaryRepository;

    public FamilyDashboardResponse getDashboardData(String userEmail, Long childId) {
        if (childId == null) {
            return FamilyDashboardResponse.builder().build();
        }

        Child child = childRepository.findById(childId)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        return FamilyDashboardResponse.builder()
                .childProfile(buildChildProfile(child))
                .sessionSummary(buildSessionSummary(child))
                .emotionalMetrics(buildEmotionalMetrics(child))
                .engagementMetrics(buildEngagementMetrics(child))
                .build();
    }

    // ── Child Profile ──

    private ChildProfileDTO buildChildProfile(Child child) {
        String lastSessionTime = child.getLastSessionAt() != null
                ? child.getLastSessionAt().format(DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm"))
                : sessionRepository.findTopByChild_IdOrderByEndTimeDesc(child.getId())
                    .map(s -> s.getEndTime() != null ? s.getEndTime().format(DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm")) : "No sessions yet")
                    .orElse("No sessions yet");

        String clinicianName = "None Assigned";
        if (child.getAssignedClinician() != null) {
            clinicianName = child.getAssignedClinician().getName();
        } else if (child.getClinician() != null && child.getClinician().getUser() != null) {
            clinicianName = child.getClinician().getUser().getName();
        }

        return ChildProfileDTO.builder()
                .name(child.getName())
                .age(child.getAge())
                .gradeLevel(child.getGradeLevel())
                .diagnosis(child.getDiagnosis())
                .assignedClinician(clinicianName)
                .therapistAssigned(clinicianName)
                .currentFocus(child.getCurrentFocusArea())
                .lastSessionTime(lastSessionTime)
                .statusBadge(child.getStatusBadge())
                .build();
    }

    // ── Session Summary ──

    private SessionSummaryDTO buildSessionSummary(Child child) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime startOfWeek = now.minusDays(now.getDayOfWeek().getValue() % 7);

        Long totalSessionsThisWeek = sessionRepository.countByChild_IdAndStartTimeAfter(child.getId(), startOfWeek);
        Long totalSessionsAllTime = sessionRepository.countByChild_Id(child.getId());

        // Get weekly summary for richer data
        LocalDate weekStart = LocalDate.now().with(java.time.DayOfWeek.MONDAY);
        Optional<WeeklySessionSummary> weeklySummary = weeklySummaryRepository.findByChildIdAndWeekStartDate(child.getId(), weekStart);

        // Today's duration
        LocalDateTime startOfDay = now.toLocalDate().atStartOfDay();
        Long todayDurationSeconds = sessionRepository.sumDurationByChildIdAndStartTimeAfter(child.getId(), startOfDay);
        if (todayDurationSeconds == null) todayDurationSeconds = 0L;

        Double avgDurationSeconds = sessionRepository.avgDurationByChildId(child.getId());
        if (avgDurationSeconds == null) avgDurationSeconds = 0.0;

        // Recent sessions for the week
        Map<String, Object> recentSessions = buildRecentSessions(child.getId());

        return SessionSummaryDTO.builder()
                .totalSessionsThisWeek(totalSessionsThisWeek)
                .totalSessionsAllTime(totalSessionsAllTime != null ? totalSessionsAllTime.intValue() : 0)
                .todaySessionDuration((todayDurationSeconds / 60) + " minutes")
                .averageSessionDuration(String.format("%.0f minutes", avgDurationSeconds / 60))
                .weeklyGoalProgress(weeklySummary.map(WeeklySessionSummary::getWeeklyGoalProgress).orElse(
                        child.getWeeklySessionGoal() != null && child.getWeeklySessionGoal() > 0
                                ? (int) Math.min(100, (totalSessionsThisWeek * 100.0) / child.getWeeklySessionGoal())
                                : 0))
                .activitiesCompletedToday(weeklySummary.map(WeeklySessionSummary::getActivitiesCompleted).orElse(0))
                .lastActivityCompleted(weeklySummary.map(WeeklySessionSummary::getMostRecentActivity).orElse(null))
                .nextScheduledSession(weeklySummary.map(ws -> ws.getNextScheduledSession() != null
                        ? ws.getNextScheduledSession().format(DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm")) : null).orElse(null))
                .recentSessions(recentSessions)
                .build();
    }

    private Map<String, Object> buildRecentSessions(Long childId) {
        Map<String, Object> recentSessions = new LinkedHashMap<>();
        LocalDateTime weekStart = LocalDateTime.now().with(java.time.DayOfWeek.MONDAY).toLocalDate().atStartOfDay();
        List<Session> sessions = sessionRepository.findByChild_IdAndStartTimeBetween(childId, weekStart, LocalDateTime.now());

        for (Session s : sessions) {
            String dayName = s.getStartTime().getDayOfWeek().name();
            dayName = dayName.substring(0, 1).toUpperCase() + dayName.substring(1).toLowerCase();
            Map<String, Object> dayData = new LinkedHashMap<>();
            dayData.put("duration", (s.getDurationSeconds() != null ? s.getDurationSeconds() / 60 : 0) + " min");
            dayData.put("mood", s.getDominantMood() != null ? capitalize(s.getDominantMood()) : "Neutral");
            dayData.put("score", s.getAvgEngagementScore() != null ? s.getAvgEngagementScore().intValue() * 100 : 0);
            recentSessions.put(dayName, dayData);
        }

        return recentSessions;
    }

    // ── Emotional Metrics ──

    private EmotionalSummaryDTO buildEmotionalMetrics(Child child) {
        // Get latest session analytics
        Optional<SessionAnalytics> latestAnalytics = analyticsRepository.findTopByChildIdOrderByCreatedAtDesc(child.getId());

        if (latestAnalytics.isEmpty()) {
            return EmotionalSummaryDTO.builder().build();
        }

        SessionAnalytics sa = latestAnalytics.get();

        // Get 7-day emotional history for chart
        List<ChildEmotionalHistory> last7Days = emotionalHistoryRepository.findTop7ByChildIdOrderByRecordedDateDesc(child.getId());
        Collections.reverse(last7Days); // Oldest first for chart

        List<Map<String, Object>> weeklyMoodData = last7Days.stream()
                .map(h -> {
                    Map<String, Object> dayData = new LinkedHashMap<>();
                    dayData.put("day", h.getRecordedDate().getDayOfWeek().name().substring(0, 3));
                    dayData.put("score", h.getMoodScore() != null ? h.getMoodScore() : 0);
                    return dayData;
                })
                .collect(Collectors.toList());

        // Emotion breakdown from latest analytics
        Map<String, Integer> emotionBreakdown = new LinkedHashMap<>();
        if (sa.getPctHappy() != null) emotionBreakdown.put("Happy", sa.getPctHappy().intValue());
        if (sa.getPctCalm() != null) emotionBreakdown.put("Calm", sa.getPctCalm().intValue());
        if (sa.getPctFocused() != null) emotionBreakdown.put("Focused", sa.getPctFocused().intValue());
        if (sa.getPctAnxious() != null) emotionBreakdown.put("Anxious", sa.getPctAnxious().intValue());
        if (sa.getPctFrustrated() != null) emotionBreakdown.put("Frustrated", sa.getPctFrustrated().intValue());
        if (sa.getPctSad() != null) emotionBreakdown.put("Sad", sa.getPctSad().intValue());

        return EmotionalSummaryDTO.builder()
                .overallMoodScore(sa.getOverallMoodScore())
                .moodTrend(sa.getMoodTrend())
                .primaryEmotion(sa.getPrimaryEmotion())
                .emotionStability(sa.getEmotionStabilityScore())
                .anxietyLevel(sa.getAnxietyLevel())
                .selfRegulationScore(sa.getSelfRegulationScore())
                .positiveInteractions(sa.getPositiveInteractions())
                .challengingMoments(sa.getChallengingMoments())
                .weeklyMoodData(weeklyMoodData)
                .emotionBreakdown(emotionBreakdown)
                .build();
    }

    // ── Engagement Metrics ──

    private EngagementSummaryDTO buildEngagementMetrics(Child child) {
        Optional<SessionAnalytics> latestAnalytics = analyticsRepository.findTopByChildIdOrderByCreatedAtDesc(child.getId());

        if (latestAnalytics.isEmpty()) {
            return EngagementSummaryDTO.builder().build();
        }

        SessionAnalytics sa = latestAnalytics.get();

        // Get 7-day engagement history for chart
        List<ChildEngagementHistory> last7Days = engagementHistoryRepository.findTop7ByChildIdOrderByRecordedDateDesc(child.getId());
        Collections.reverse(last7Days);

        List<Map<String, Object>> weeklyFocusData = last7Days.stream()
                .map(h -> {
                    Map<String, Object> dayData = new LinkedHashMap<>();
                    dayData.put("day", h.getRecordedDate().getDayOfWeek().name().substring(0, 3));
                    dayData.put("focus", h.getFocusScore() != null ? h.getFocusScore() : 0);
                    dayData.put("attention", h.getAttentionSpanMinutes() != null ? h.getAttentionSpanMinutes().intValue() : 0);
                    return dayData;
                })
                .collect(Collectors.toList());

        // Top activities
        List<ChildActivityPerformance> activities = activityPerformanceRepository.findByChildIdOrderByAvgScoreDesc(child.getId());
        List<Map<String, Object>> topActivities = activities.stream()
                .limit(4)
                .map(a -> {
                    Map<String, Object> actData = new LinkedHashMap<>();
                    actData.put("name", a.getActivityName());
                    actData.put("score", a.getScore());
                    actData.put("completions", a.getCompletionCount());
                    return actData;
                })
                .collect(Collectors.toList());

        return EngagementSummaryDTO.builder()
                .focusScore(sa.getFocusScore())
                .attentionSpanMinutes(sa.getAttentionSpanMinutes() != null ? sa.getAttentionSpanMinutes().intValue() : null)
                .taskCompletionRate(sa.getTaskCompletionRate())
                .participationLevel(sa.getParticipationLevel())
                .distractionFrequency(sa.getDistractionFrequency())
                .responsiveness(sa.getResponsivenessScore())
                .initiativeTaking(sa.getInitiativeTakingScore())
                .collaborationScore(sa.getCollaborationScore())
                .weeklyFocusData(weeklyFocusData)
                .topActivities(topActivities)
                .build();
    }

    // ── Helpers ──

    private String capitalize(String s) {
        if (s == null || s.isEmpty()) return s;
        return s.substring(0, 1).toUpperCase() + s.substring(1).toLowerCase();
    }
}
