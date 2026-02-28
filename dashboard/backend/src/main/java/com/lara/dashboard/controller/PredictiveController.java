package com.lara.dashboard.controller;

import com.lara.dashboard.dto.PredictiveRiskDto;
import com.lara.dashboard.service.PredictiveAnalyticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/predictive")
@RequiredArgsConstructor
public class PredictiveController {

    private final PredictiveAnalyticsService predictiveAnalyticsService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<PredictiveRiskDto> getPredictiveMetrics(@PathVariable String userId) {
        return ResponseEntity.ok(predictiveAnalyticsService.computePredictiveRisks(userId));
    }
}
