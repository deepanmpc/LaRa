package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ZpdOverviewDto;
import com.lara.dashboard.service.ZpdAnalyticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/zpd")
@RequiredArgsConstructor
public class ZpdController {

    private final ZpdAnalyticsService zpdAnalyticsService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'EDUCATOR', 'ADMIN')")
    public ResponseEntity<ZpdOverviewDto> getZpdMetrics(
            @PathVariable String userId,
            @RequestParam(defaultValue = "30") int daysRange) {
        
        return ResponseEntity.ok(zpdAnalyticsService.getZpdAnalytics(userId, daysRange));
    }
}
