package com.lara.dashboard.controller;

import com.lara.dashboard.service.ToolIntelligenceService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/tools")
@RequiredArgsConstructor
public class ToolInterventionController {

    private final ToolIntelligenceService toolIntelligenceService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'EDUCATOR', 'ADMIN')")
    public ResponseEntity<Map<String, Object>> getToolAnalytics(
            @PathVariable String userId,
            @RequestParam(defaultValue = "30") int daysRange) {
        
        return ResponseEntity.ok(toolIntelligenceService.getToolAnalytics(userId, daysRange));
    }
}
