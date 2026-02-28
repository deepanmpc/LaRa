package com.lara.dashboard.controller;

import com.lara.dashboard.dto.CalibrationMetricsDto;
import com.lara.dashboard.service.CalibrationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/calibration")
@RequiredArgsConstructor
public class CalibrationController {

    private final CalibrationService calibrationService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<CalibrationMetricsDto> getCalibrationData(
            @PathVariable String userId,
            @RequestParam(defaultValue = "FRUSTRATION_ESCALATION") String type) {
        return ResponseEntity.ok(calibrationService.getCalibrationMetrics(userId, type));
    }
}
