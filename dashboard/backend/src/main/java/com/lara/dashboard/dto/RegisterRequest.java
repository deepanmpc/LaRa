package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RegisterRequest {
    private String name;
    private String email;
    private String password;
    private String role; // "ROLE_FAMILY" or "ROLE_CLINICIAN"

    // Optional clinician fields
    private String licenseNumber;
    private String specialization;
    private Integer yearsOfExperience;
}
