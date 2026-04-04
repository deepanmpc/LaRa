package com.lara.dashboard.service;

import com.lara.dashboard.dto.ChildProfileDTO;
import com.lara.dashboard.dto.EmotionalSummaryDTO;
import com.lara.dashboard.dto.EngagementSummaryDTO;
import com.lara.dashboard.dto.FamilyDashboardResponse;
import com.lara.dashboard.dto.SessionSummaryDTO;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.EmotionalMetric;
import com.lara.dashboard.entity.Session;
import com.lara.dashboard.entity.ToolIntervention;
import com.lara.dashboard.entity.ZpdMetric;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.SessionRepository;
import com.lara.dashboard.repository.EmotionalMetricRepository;
import com.lara.dashboard.repository.ZpdMetricRepository;
import com.lara.dashboard.repository.ToolInterventionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.DayOfWeek;
import java.time.format.TextStyle;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class FamilyDashboardService {

    private final ChildRepository childRepository;
    private final SessionRepository sessionRepository;
    private final EmotionalMetricRepository emotionalMetricRepository;
    private final ZpdMetricRepository zpdMetricRepository;
    private final ToolInterventionRepository toolInterventionRepository;

    private String getChildIdHashed(Long childId) {
        try {
            MessageDigest md = MessageDigest.getInstance("SHA-256");
            byte[] hash = md.digest(String.valueOf(childId).getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("SHA-256 not found", e);
        }
    }

    public FamilyDashboardResponse getDashboardData(String userEmail, Long childId) {
        Child child = childRepository.findById(childId).orElse(null);
        String childIdHashed = getChildIdHashed(childId);

        return FamilyDashboardResponse.builder()
                .childProfile(buildChildProfile(child))
                .sessionSummary(buildSessionSummary(childId, childIdHashed))
                .emotionalMetrics(buildEmotionalMetrics(childIdHashed))
                .engagementMetrics(buildEngagementMetrics(childIdHashed))
                .build();
    }

    private ChildProfileDTO buildChildProfile(Child child) {
        if (child == null) {
            return new ChildProfileDTO();
        }
        
        String lastSessionTime = sessionRepository.findTopByChild_IdOrderByEndTimeDesc(child.getId())
                .map(s -> s.getEndTime().toString())
                .orElse("No sessions yet");

        return ChildProfileDTO.builder()
                .name(child.getName())
                .age(child.getAge())
                .gradeLevel(child.getGradeLevel())
                .therapistAssigned(child.getClinician() != null && child.getClinician().getUser() != null ? child.getClinician().getUser().getName() : null)
                .lastSessionTime(lastSessionTime)
                .currentFocus(null)
                .statusBadge(null)
                .build();
    }

    private SessionSummaryDTO buildSessionSummary(Long childId, String childIdHashed) {
        LocalDateTime startOfWeek = LocalDate.now().with(java.time.temporal.TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY)).atStartOfDay();
        LocalDateTime startOfDay = LocalDate.now().atStartOfDay();

        Long totalSessionsThisWeek = sessionRepository.countByChild_IdAndStartTimeAfter(childId, startOfWeek);
        if (totalSessionsThisWeek == null) totalSessionsThisWeek = 0L;
        
        Long totalSessionsAllTime = sessionRepository.countByChild_Id(childId);
        if (totalSessionsAllTime == null) totalSessionsAllTime = 0L;

        Long todayDuration = sessionRepository.sumDurationByChildIdAndStartTimeAfter(childId, startOfDay);
        String todaySessionDuration = (todayDuration != null ? (todayDuration / 60) : 0) + " minutes";

        Double avgDuration = sessionRepository.avgDurationByChildId(childId);
        String averageSessionDuration = (avgDuration != null ? (Math.round(avgDuration) / 60) : 0) + " minutes";

        Long activitiesCompletedToday = toolInterventionRepository.countByChildIdHashedAndTimestampAfter(childIdHashed, startOfDay);
        if (activitiesCompletedToday == null) activitiesCompletedToday = 0L;

        int weeklyGoalProgress = Math.min(100, (int) Math.round((totalSessionsThisWeek / 5.0) * 100));

        String lastActivityCompleted = toolInterventionRepository.findTopByChildIdHashedOrderByTimestampDesc(childIdHashed)
                .map(ToolIntervention::getToolId)
                .orElse(null);

        return SessionSummaryDTO.builder()
                .totalSessionsThisWeek(totalSessionsThisWeek)
                .totalSessionsAllTime(totalSessionsAllTime.intValue())
                .todaySessionDuration(todaySessionDuration)
                .averageSessionDuration(averageSessionDuration)
                .activitiesCompletedToday(activitiesCompletedToday.intValue())
                .weeklyGoalProgress(weeklyGoalProgress)
                .lastActivityCompleted(lastActivityCompleted)
                .nextScheduledSession(null)
                .recentSessions(new HashMap<>())
                .build();
    }

    private EmotionalSummaryDTO buildEmotionalMetrics(String childIdHashed) {
        LocalDateTime sevenDaysAgo = LocalDateTime.now().minusDays(7);
        List<EmotionalMetric> weekMetrics = emotionalMetricRepository.findByChildIdHashedAndTimestampAfter(childIdHashed, sevenDaysAgo);

        if (weekMetrics.isEmpty()) {
            return new EmotionalSummaryDTO();
        }

        int overallMoodScore = (int) Math.round(weekMetrics.stream().mapToDouble(EmotionalMetric::getMoodScore).average().orElse(0));

        Map<String, Long> primaryCounts = weekMetrics.stream()
                .filter(m -> m.getPrimaryEmotion() != null)
                .collect(Collectors.groupingBy(EmotionalMetric::getPrimaryEmotion, Collectors.counting()));
        
        String primaryEmotion = primaryCounts.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(null);

        LocalDateTime threeDaysAgo = LocalDateTime.now().minusDays(3);
        LocalDateTime sixDaysAgo = LocalDateTime.now().minusDays(6);
        double currentAvg = weekMetrics.stream().filter(m -> m.getTimestamp().isAfter(threeDaysAgo)).mapToDouble(EmotionalMetric::getMoodScore).average().orElse(0);
        double previousAvg = weekMetrics.stream().filter(m -> m.getTimestamp().isAfter(sixDaysAgo) && m.getTimestamp().isBefore(threeDaysAgo)).mapToDouble(EmotionalMetric::getMoodScore).average().orElse(currentAvg);

        String moodTrend = "Stable";
        if (currentAvg > previousAvg + 5) moodTrend = "Improving";
        else if (currentAvg < previousAvg - 5) moodTrend = "Needs Support";

        List<Map<String, Object>> weeklyMoodData = new ArrayList<>();
        Map<DayOfWeek, Double> byDay = weekMetrics.stream().collect(Collectors.groupingBy(m -> m.getTimestamp().getDayOfWeek(), Collectors.averagingDouble(EmotionalMetric::getMoodScore)));
        for (DayOfWeek day : DayOfWeek.values()) {
            if (byDay.containsKey(day)) {
                Map<String, Object> map = new HashMap<>();
                map.put("day", day.getDisplayName(TextStyle.SHORT, Locale.ENGLISH));
                map.put("score", (int) Math.round(byDay.get(day)));
                weeklyMoodData.add(map);
            }
        }

        LocalDateTime thirtyDaysAgo = LocalDateTime.now().minusDays(30);
        List<Object[]> breakdownData = emotionalMetricRepository.findEmotionBreakdown(childIdHashed, thirtyDaysAgo);
        long total30 = breakdownData.stream().mapToLong(row -> (Long) row[1]).sum();
        Map<String, Integer> emotionBreakdown = new HashMap<>();
        for (Object[] row : breakdownData) {
            String emotion = (String) row[0];
            long count = (Long) row[1];
            emotionBreakdown.put(emotion, (int) Math.round((count * 100.0) / total30));
        }

        long positiveInteractions = weekMetrics.stream().filter(m -> Arrays.asList("Happy", "Calm", "Focused").contains(m.getPrimaryEmotion())).count();
        long challengingMoments = weekMetrics.stream().filter(m -> Arrays.asList("Anxious", "Frustrated").contains(m.getPrimaryEmotion())).count();

        return EmotionalSummaryDTO.builder()
                .overallMoodScore(overallMoodScore)
                .primaryEmotion(primaryEmotion)
                .moodTrend(moodTrend)
                .weeklyMoodData(weeklyMoodData)
                .emotionBreakdown(emotionBreakdown)
                .anxietyLevel(null)
                .selfRegulationScore(null)
                .positiveInteractions((int) positiveInteractions)
                .challengingMoments((int) challengingMoments)
                .build();
    }

    private EngagementSummaryDTO buildEngagementMetrics(String childIdHashed) {
        LocalDateTime sevenDaysAgo = LocalDateTime.now().minusDays(7);
        List<ZpdMetric> weekZpd = zpdMetricRepository.findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(childIdHashed, sevenDaysAgo);

        if (weekZpd.isEmpty()) {
            return new EngagementSummaryDTO();
        }

        int focusScore = (int) Math.round(weekZpd.stream().mapToDouble(ZpdMetric::getScore).average().orElse(0));

        List<Map<String, Object>> weeklyFocusData = new ArrayList<>();
        Map<DayOfWeek, Double> byDay = weekZpd.stream().collect(Collectors.groupingBy(m -> m.getTimestamp().getDayOfWeek(), Collectors.averagingDouble(ZpdMetric::getScore)));
        for (DayOfWeek day : DayOfWeek.values()) {
            if (byDay.containsKey(day)) {
                Map<String, Object> map = new HashMap<>();
                map.put("day", day.getDisplayName(TextStyle.SHORT, Locale.ENGLISH));
                map.put("focus", (int) Math.round(byDay.get(day)));
                weeklyFocusData.add(map);
            }
        }

        List<ToolIntervention> allTools = toolInterventionRepository.findAll();
        Map<String, Long> toolCounts = allTools.stream()
                .filter(t -> childIdHashed.equals(t.getChildIdHashed()) && t.getToolId() != null)
                .collect(Collectors.groupingBy(ToolIntervention::getToolId, Collectors.counting()));

        List<Map<String, Object>> topActivities = toolCounts.entrySet().stream()
                .sorted((e1, e2) -> e2.getValue().compareTo(e1.getValue()))
                .limit(4)
                .map(e -> {
                    Map<String, Object> map = new HashMap<>();
                    map.put("name", e.getKey());
                    map.put("completions", e.getValue().intValue());
                    map.put("score", focusScore);
                    return map;
                })
                .collect(Collectors.toList());

        return EngagementSummaryDTO.builder()
                .focusScore(focusScore)
                .weeklyFocusData(weeklyFocusData)
                .topActivities(topActivities)
                .taskCompletionRate(null)
                .build();
    }
}
