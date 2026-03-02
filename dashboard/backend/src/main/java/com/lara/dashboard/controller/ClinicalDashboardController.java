package com.lara.dashboard.controller;

import com.lara.dashboard.dto.clinical.ClinicalDashboardDTO;
import com.lara.dashboard.service.ClinicalDashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/api/dashboard/clinical")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173")
public class ClinicalDashboardController {

    private final ClinicalDashboardService clinicalDashboardService;

    @GetMapping("/{studentId}")
    @PreAuthorize("hasRole('CLINICIAN')")
    public ResponseEntity<ClinicalDashboardDTO> getClinicalDashboard(
            @PathVariable String studentId,
            @RequestParam(defaultValue = "30") int daysRange) {
        
        if (studentId == null || studentId.trim().isEmpty()) {
            return ResponseEntity.badRequest().build();
        }

        Optional<ClinicalDashboardDTO> responseOpt = clinicalDashboardService.getClinicalDashboard(studentId, daysRange);

        return responseOpt.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
