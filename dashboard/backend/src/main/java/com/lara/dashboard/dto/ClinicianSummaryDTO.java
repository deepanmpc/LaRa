package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ClinicianSummaryDTO {
    private Long id;          // ClinicianProfile.id (NOT User.id)
    private String name;      // clinician's user name
    private String organization;
    private String specialization;
}
