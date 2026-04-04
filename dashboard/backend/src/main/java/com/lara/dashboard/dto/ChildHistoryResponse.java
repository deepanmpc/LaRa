package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.util.List;
import java.util.Map;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildHistoryResponse {
    private Long childId;
    private String childName;
    private List<SessionBriefDTO> recentSessions;
    private List<Map<String, Object>> learningProgress;
    private List<Map<String, Object>> emotionalHistory;
    private EngagementSummaryDTO engagementOverview;
}

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
class SessionBriefDTO {
    private Long id;
    private String sessionUuid;
    private String startTime;
    private Integer durationSeconds;
    private String dominantMood;
    private Double avgEngagement;
}
