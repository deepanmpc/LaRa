package com.lara.dashboard.controller;

import com.lara.dashboard.dto.SystemPerformanceDto;
import com.lara.dashboard.dto.ModelHealthDto;
import com.lara.dashboard.dto.BiasMonitoringDto;
import com.lara.dashboard.service.SystemPerformanceService;
import com.lara.dashboard.service.MetaLearningService;
import com.lara.dashboard.service.BiasMonitoringService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/diagnostics")
@RequiredArgsConstructor
public class DiagnosticsController {

    private final SystemPerformanceService systemPerformanceService;
    private final MetaLearningService metaLearningService;
    private final BiasMonitoringService biasMonitoringService;

    @GetMapping("/system-performance")
    @PreAuthorize("hasAnyRole('RESEARCHER', 'ADMIN')")
    public ResponseEntity<SystemPerformanceDto> getSystemPerformance() {
        return ResponseEntity.ok(systemPerformanceService.assessSystemPerformance());
    }

    @GetMapping("/model-health")
    @PreAuthorize("hasAnyRole('RESEARCHER', 'ADMIN')")
    public ResponseEntity<ModelHealthDto> getModelHealth() {
        return ResponseEntity.ok(metaLearningService.evaluateMetaLearningHealth());
    }

    @GetMapping("/bias-monitoring")
    @PreAuthorize("hasAnyRole('RESEARCHER', 'ADMIN')")
    public ResponseEntity<BiasMonitoringDto> getBiasMonitoring() {
        return ResponseEntity.ok(biasMonitoringService.evaluateGroupFairness());
    }
}
