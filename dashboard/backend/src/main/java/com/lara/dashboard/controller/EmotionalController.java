package com.lara.dashboard.controller;

import com.lara.dashboard.dto.EmotionalOverviewDto;
import com.lara.dashboard.service.EmotionalAnalyticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/emotional")
@RequiredArgsConstructor
public class EmotionalController {

    private final EmotionalAnalyticsService emotionalAnalyticsService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<EmotionalOverviewDto> getEmotionalMetrics(
            @PathVariable String userId,
            @RequestParam(defaultValue = "30") int daysRange) {
        
        return ResponseEntity.ok(emotionalAnalyticsService.getEmotionalMetrics(userId, daysRange));
    }
}
