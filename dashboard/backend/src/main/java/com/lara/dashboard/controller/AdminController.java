package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ClinicianResponse;
import com.lara.dashboard.dto.ChildResponse;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.service.AdminService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminController {

    private final AdminService adminService;
    private final com.lara.dashboard.service.SystemHealthService systemHealthService;

    @GetMapping("/health")
    public com.lara.dashboard.dto.SystemHealthResponse health() {
        return systemHealthService.getHealth();
    }

    @GetMapping("/clinicians/pending")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<List<ClinicianResponse>> getPendingClinicians() {
        return ResponseEntity.ok(adminService.getPendingClinicians());
    }

    @PostMapping("/clinicians/{id}/approve")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<?> approveClinician(@PathVariable Long id) {
        try {
            adminService.approveClinician(id);
            return ResponseEntity.ok(Map.of("message", "Clinician approved successfully"));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/clinicians/{id}/reject")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<?> rejectClinician(@PathVariable Long id) {
        try {
            adminService.rejectClinician(id);
            return ResponseEntity.ok(Map.of("message", "Clinician rejected successfully"));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @GetMapping("/users")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<List<User>> getAllUsers() {
        return ResponseEntity.ok(adminService.getAllUsers());
    }

    @GetMapping("/children")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<List<ChildResponse>> getAllChildren() {
        return ResponseEntity.ok(adminService.getAllChildren());
    }

    @GetMapping("/system")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getSystemMetrics() {
        return ResponseEntity.ok(adminService.getSystemMetrics());
    }

    @GetMapping("/logs")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<List<com.lara.dashboard.entity.ActivityLog>> getLogs() {
        return ResponseEntity.ok(adminService.getLogs());
    }
}
