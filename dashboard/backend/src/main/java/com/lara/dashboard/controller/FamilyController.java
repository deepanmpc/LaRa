package com.lara.dashboard.controller;

import com.lara.dashboard.dto.FamilyDashboardResponse;
import com.lara.dashboard.service.MockFamilyDashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/family")
@RequiredArgsConstructor
public class FamilyController {

    private final MockFamilyDashboardService dashboardService;

    @GetMapping("/dashboard")
    public ResponseEntity<FamilyDashboardResponse> getDashboard(Authentication authentication) {
        String email = authentication.getName();
        FamilyDashboardResponse response = dashboardService.getDashboardData(email);
        return ResponseEntity.ok(response);
    }
}
