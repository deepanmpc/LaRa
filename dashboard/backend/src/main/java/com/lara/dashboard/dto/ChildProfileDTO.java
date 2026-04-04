package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildProfileDTO {
    private String name;
    private Integer age;
    private String gradeLevel;
    private String diagnosis;
    private String assignedClinician;
    private String therapistAssigned;
    private String currentFocus;
    private String lastSessionTime;
    private String statusBadge;
}
