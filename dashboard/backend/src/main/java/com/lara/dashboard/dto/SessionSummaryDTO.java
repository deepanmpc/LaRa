package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionSummaryDTO {
    private Long totalSessionsThisWeek;
    private Integer totalSessionsAllTime;
    private String todaySessionDuration;
    private String averageSessionDuration;
    private String lastActivityCompleted;
    private String nextScheduledSession;
    private Integer weeklyGoalProgress;
    private Integer activitiesCompletedToday;
    private Map<String, Object> recentSessions;
}
