package com.lara.dashboard.controller;

import com.lara.dashboard.dto.CausalityMatrixDto;
import com.lara.dashboard.service.CausalityAnalyticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/causality")
@RequiredArgsConstructor
public class CausalityController {

    private final CausalityAnalyticsService causalityAnalyticsService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<CausalityMatrixDto> getTemporalCausality(@PathVariable String userId) {
        return ResponseEntity.ok(causalityAnalyticsService.computeTemporalCausality(userId));
    }
}
