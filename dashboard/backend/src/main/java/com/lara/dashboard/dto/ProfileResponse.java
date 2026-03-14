package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ProfileResponse {
    private String name;
    private String email;
    private String role;
    
    // clinician-only fields
    private String organization;
    private String specialization;
    private String licenseNumber;
}
