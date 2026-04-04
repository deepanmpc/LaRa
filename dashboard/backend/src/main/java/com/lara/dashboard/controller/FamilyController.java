package com.lara.dashboard.controller;

import com.lara.dashboard.dto.FamilyDashboardResponse;
import com.lara.dashboard.service.FamilyDashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/family")
@RequiredArgsConstructor
public class FamilyController {

    private final FamilyDashboardService dashboardService;
    private final com.lara.dashboard.service.SessionService sessionService;

    @GetMapping({"/dashboard", "/dashboard/{childId}"})
    public ResponseEntity<FamilyDashboardResponse> getDashboard(Authentication authentication, @PathVariable(required = false) Long childId) {
        String email = authentication.getName();
        FamilyDashboardResponse response = dashboardService.getDashboardData(email, childId);
        return ResponseEntity.ok(response);
    }

    @PostMapping("/session/start")
    public ResponseEntity<java.util.Map<String, String>> startSession(@RequestBody java.util.Map<String, Object> payload) {
        String sessionUuid = java.util.UUID.randomUUID().toString();
        java.util.Map<String, String> response = new java.util.HashMap<>();
        response.put("sessionUuid", sessionUuid);
        response.put("status", "STARTED");
        return ResponseEntity.ok(response);
    }

    @PostMapping("/session/end")
    public ResponseEntity<java.util.Map<String, String>> endSession(@RequestBody com.lara.dashboard.dto.SessionEndRequest request) {
        sessionService.saveSessionEnd(request);
        java.util.Map<String, String> response = new java.util.HashMap<>();
        response.put("status", "SAVED");
        return ResponseEntity.ok(response);
    }
}
