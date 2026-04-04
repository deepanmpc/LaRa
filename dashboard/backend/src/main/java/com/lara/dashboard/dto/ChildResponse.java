package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildResponse {
    private Long id;
    private String name;
    private Integer age;
    private String gradeLevel;
    private String lastSessionDate;
    private Long clinicianId;
    private String clinicianName;
    private String clinicianOrganization;
    private String diagnosis;
    private String notes;
    private String avatarColor;
    private String statusBadge;
    private String currentFocusArea;
    private Integer weeklySessionGoal;
    private String lastSessionAt;
}
