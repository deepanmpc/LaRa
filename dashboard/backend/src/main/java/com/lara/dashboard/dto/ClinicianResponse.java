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
public class ClinicianResponse {
    private Long id; // User ID
    private String name;
    private String email;
    private String phone;
    private String organization;
    private String specialization;
    private String licenseNumber;
    private Integer yearsOfExperience;
    private String status;
    private LocalDateTime createdAt;
}
