package com.lara.dashboard.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@Slf4j
public class AuditLoggingService {

    /**
     * Enforces Requirement 11: Audit logging of clinician views.
     * Logs exactly who views which student's Tier 2 analytics and when.
     */
    public void logClinicalAccess(String clinicianId, String studentIdHashed, String action) {
        log.info("AUDIT LOG: Clinician [{}] performed [{}] on Student [{}] at [{}]",
                clinicianId, action, studentIdHashed, LocalDateTime.now());
        // In a production environment, this would persist to an `AuditLog` database table
        // to strictly monitor HIPAA / privacy compliance access.
    }
}
