package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionBriefDTO {
    private Long id;
    private String sessionUuid;
    private String startTime;
    private Integer durationSeconds;
    private String dominantMood;
    private Double avgEngagement;
}