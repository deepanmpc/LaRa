package com.lara.dashboard.service;

import com.lara.dashboard.dto.*;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.EmotionalMetric;
import com.lara.dashboard.entity.Session;
import com.lara.dashboard.entity.ToolIntervention;
import com.lara.dashboard.entity.ZpdMetric;
import com.lara.dashboard.repository.*;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
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
    private final ZpdMetricRepository zpdMetricRepository;
    private final ToolInterventionRepository toolInterventionRepository;

    public FamilyDashboardResponse getDashboardData(String userEmail, Long childId) {
        if (childId == null) {
            return FamilyDashboardResponse.builder().build();
        }

        Child child = childRepository.findById(childId)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        String childIdHashed = hashChildId(childId);

        return FamilyDashboardResponse.builder()
                .childProfile(buildChildProfile(child))
                .sessionSummary(buildSessionSummary(childId, childIdHashed))
                .emotionalMetrics(buildEmotionalMetrics(childIdHashed))
                .engagementMetrics(buildEngagementMetrics(childIdHashed))
                .build();
    }

    private ChildProfileDTO buildChildProfile(Child child) {
        String lastSessionTime = sessionRepository.findTopByChild_IdOrderByEndTimeDesc(child.getId())
                .map(s -> s.getEndTime() != null ? s.getEndTime().format(DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm")) : "No sessions yet")
                .orElse("No sessions yet");

        return ChildProfileDTO.builder()
                .name(child.getName())
                .age(child.getAge())
                .gradeLevel(child.getGradeLevel())
                .therapistAssigned(child.getClinician() != null && child.getClinician().getUser() != null 
                        ? child.getClinician().getUser().getName() : "None Assigned")
                .lastSessionTime(lastSessionTime)
                .currentFocus(null) // Real data not in schema yet
                .statusBadge(null)  // Real data not in schema yet
                .build();
    }

    private SessionSummaryDTO buildSessionSummary(Long childId, String childIdHashed) {
        LocalDateTime now = LocalDateTime.now();
        LocalDateTime startOfWeek = now.minusDays(now.getDayOfWeek().getValue() % 7);
        LocalDateTime startOfDay = now.toLocalDate().atStartOfDay();

        Long totalSessionsThisWeek = sessionRepository.countByChild_IdAndStartTimeAfter(childId, startOfWeek);
        Long totalSessionsAllTime = sessionRepository.countByChild_Id(childId);
        
        Long todayDurationSeconds = sessionRepository.sumDurationByChildIdAndStartTimeAfter(childId, startOfDay);
        if (todayDurationSeconds == null) todayDurationSeconds = 0L;
        
        Double avgDurationSeconds = sessionRepository.avgDurationByChildId(childId);
        if (avgDurationSeconds == null) avgDurationSeconds = 0.0;

        Long activitiesToday = toolInterventionRepository.countByChildIdHashedAndTimestampAfter(childIdHashed, startOfDay);
        
        Optional<ToolIntervention> lastTool = toolInterventionRepository.findTopByChildIdHashedOrderByTimestampDesc(childIdHashed);

        return SessionSummaryDTO.builder()
                .totalSessionsThisWeek(totalSessionsThisWeek)
                .totalSessionsAllTime(totalSessionsAllTime.intValue())
                .todaySessionDuration((todayDurationSeconds / 60) + " minutes")
                .averageSessionDuration(String.format("%.1f minutes", avgDurationSeconds / 60))
                .activitiesCompletedToday(activitiesToday.intValue())
                .weeklyGoalProgress((int) Math.min(100, (totalSessionsThisWeek / 5.0) * 100))
                .lastActivityCompleted(lastTool.map(ToolIntervention::getToolId).orElse(null))
                .nextScheduledSession(null)
                .build();
    }

    private EmotionalSummaryDTO buildEmotionalMetrics(String childIdHashed) {
        LocalDateTime sevenDaysAgo = LocalDateTime.now().minusDays(7);
        LocalDateTime thirtyDaysAgo = LocalDateTime.now().minusDays(30);

        List<EmotionalMetric> last7Days = emotionalMetricRepository.findByChildIdHashedAndTimestampAfter(childIdHashed, sevenDaysAgo);
        
        if (last7Days.isEmpty()) {
            return EmotionalSummaryDTO.builder().build();
        }

        double avgMood = last7Days.stream().mapToInt(EmotionalMetric::getMoodScore).average().orElse(0.0);
        
        Map<String, Long> counts = last7Days.stream()
                .collect(Collectors.groupingBy(EmotionalMetric::getPrimaryEmotion, Collectors.counting()));
        
        String primary = counts.entrySet().stream()
                .max(Map.Entry.comparingByValue())
                .map(Map.Entry::getKey)
                .orElse(null);

        // Mood Trend
        LocalDateTime threeDaysAgo = LocalDateTime.now().minusDays(3);
        LocalDateTime sixDaysAgo = LocalDateTime.now().minusDays(6);
        
        double currentAvg = last7Days.stream()
                .filter(m -> m.getTimestamp().isAfter(threeDaysAgo))
                .mapToInt(EmotionalMetric::getMoodScore).average().orElse(0.0);
        
        double previousAvg = last7Days.stream()
                .filter(m -> m.getTimestamp().isAfter(sixDaysAgo) && m.getTimestamp().isBefore(threeDaysAgo))
                .mapToInt(EmotionalMetric::getMoodScore).average().orElse(0.0);
        
        String moodTrend = "Stable";
        if (currentAvg > previousAvg + 5) moodTrend = "Improving";
        else if (currentAvg < previousAvg - 5) moodTrend = "Needs Support";

        // Emotion Breakdown last 30 days
        List<Object[]> breakdownData = emotionalMetricRepository.findEmotionBreakdown(childIdHashed, thirtyDaysAgo);
        long total30Days = breakdownData.stream().mapToLong(row -> (Long) row[1]).sum();
        Map<String, Integer> breakdown = new HashMap<>();
        for (Object[] row : breakdownData) {
            String emotion = (String) row[0];
            Long count = (Long) row[1];
            breakdown.put(emotion, (int) (count * 100 / total30Days));
        }

        long positiveCount = last7Days.stream()
                .filter(m -> Arrays.asList("Happy", "Calm", "Focused").contains(m.getPrimaryEmotion()))
                .count();
        
        long challengingCount = last7Days.stream()
                .filter(m -> Arrays.asList("Anxious", "Frustrated").contains(m.getPrimaryEmotion()))
                .count();

        return EmotionalSummaryDTO.builder()
                .overallMoodScore((int) avgMood)
                .primaryEmotion(primary)
                .moodTrend(moodTrend)
                .emotionBreakdown(breakdown)
                .positiveInteractions((int) positiveCount)
                .challengingMoments((int) challengingCount)
                .build();
    }

    private EngagementSummaryDTO buildEngagementMetrics(String childIdHashed) {
        LocalDateTime sevenDaysAgo = LocalDateTime.now().minusDays(7);
        List<ZpdMetric> metrics = zpdMetricRepository.findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(childIdHashed, sevenDaysAgo);
        
        if (metrics.isEmpty()) {
            return EngagementSummaryDTO.builder().build();
        }

        double avgFocus = metrics.stream().mapToInt(ZpdMetric::getScore).average().orElse(0.0);

        return EngagementSummaryDTO.builder()
                .focusScore((int) avgFocus)
                .build();
    }

    private String hashChildId(Long childId) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] encodedhash = digest.digest(String.valueOf(childId).getBytes(StandardCharsets.UTF_8));
            StringBuilder hexString = new StringBuilder(2 * encodedhash.length);
            for (byte b : encodedhash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) hexString.append('0');
                hexString.append(hex);
            }
            return hexString.toString();
        } catch (NoSuchAlgorithmException e) {
            throw new RuntimeException("Error hashing child ID", e);
        }
    }
}
