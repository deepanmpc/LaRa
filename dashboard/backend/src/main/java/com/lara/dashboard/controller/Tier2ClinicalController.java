package com.lara.dashboard.controller;

import com.lara.dashboard.dto.tier2.Tier2FullDashboardDto;
import com.lara.dashboard.service.AuditLoggingService;
import com.lara.dashboard.service.Tier2ClinicalService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/tier2/clinical")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "http://localhost:5173")
public class Tier2ClinicalController {

    private final Tier2ClinicalService tier2ClinicalService;
    private final AuditLoggingService auditLoggingService;

    /**
     * Requirement 11: Visible ONLY to ROLE_CLINICIAN.
     * Requirement 1-9: Returns the comprehensive clinical spec.
     */
    @GetMapping("/{studentId}")
    @PreAuthorize("hasRole('CLINICIAN')")
    public ResponseEntity<com.lara.dashboard.dto.tier2.HybridClinicalDashboardDto> getHybridClinicalDashboard(@PathVariable String studentId) {
        // Enforce Requirement 11: Audit logging of clinician views
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String clinicianId = (auth != null) ? auth.getName() : "UNKNOWN_CLINICIAN";
        
        auditLoggingService.logClinicalAccess(clinicianId, studentId, "VIEW_HYBRID_CLINICAL_DASHBOARD");

        return ResponseEntity.ok(tier2ClinicalService.getHybridDashboard(studentId));
    }

    /**
     * Requirement 10: Export & Reporting (Generate Clinical Summary PDF / CSV)
     */
    @GetMapping("/{studentId}/export")
    @PreAuthorize("hasRole('CLINICIAN')")
    public ResponseEntity<byte[]> exportClinicalData(
            @PathVariable String studentId,
            @RequestParam(defaultValue = "pdf") String format) {

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String clinicianId = (auth != null) ? auth.getName() : "UNKNOWN_CLINICIAN";
        auditLoggingService.logClinicalAccess(clinicianId, studentId, "EXPORT_TIER2_" + format.toUpperCase());

        byte[] reportBytes;
        String contentType;
        String fileExtension;

        // Mocking the byte generation for the scope of the backend response
        if ("csv".equalsIgnoreCase(format)) {
            String csvContent = "Time,Volatility,Recovery\n10:00,4.2,45.5\n10:15,3.8,40.0";
            reportBytes = csvContent.getBytes();
            contentType = "text/csv";
            fileExtension = ".csv";
        } else { // default to PDF
            reportBytes = "Mock PDF Content representing Tier 2 Clinical Analytics".getBytes();
            contentType = MediaType.APPLICATION_PDF_VALUE;
            fileExtension = ".pdf";
        }

        HttpHeaders headers = new HttpHeaders();
        headers.set(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=clinical_report_" + studentId + fileExtension);
        headers.set(HttpHeaders.CONTENT_TYPE, contentType);

        return ResponseEntity.ok()
                .headers(headers)
                .body(reportBytes);
    }
}
