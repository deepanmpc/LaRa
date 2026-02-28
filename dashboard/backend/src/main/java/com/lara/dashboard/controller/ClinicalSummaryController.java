package com.lara.dashboard.controller;

import com.lara.dashboard.dto.CognitiveSummaryDto;
import com.lara.dashboard.service.ClinicalSummaryService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/clinical-summary")
@RequiredArgsConstructor
public class ClinicalSummaryController {

    private final ClinicalSummaryService clinicalSummaryService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<CognitiveSummaryDto> getClinicalSummary(@PathVariable String userId) {
        return ResponseEntity.ok(clinicalSummaryService.generateSummary(userId));
    }
}
