package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ZpdOverviewDto;
import com.lara.dashboard.service.OverviewService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/overview")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173")
public class OverviewController {

    private final OverviewService overviewService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<ZpdOverviewDto> getZpdOverview(@PathVariable String userId) {
        return ResponseEntity.ok(overviewService.getOverviewData(userId));
    }
}
