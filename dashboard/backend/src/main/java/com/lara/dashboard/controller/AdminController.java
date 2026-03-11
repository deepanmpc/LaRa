package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ClinicianResponse;
import com.lara.dashboard.service.AdminService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/admin/clinicians")
@RequiredArgsConstructor
public class AdminController {

    private final AdminService adminService;

    @GetMapping("/pending")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<List<ClinicianResponse>> getPendingClinicians() {
        return ResponseEntity.ok(adminService.getPendingClinicians());
    }

    @PostMapping("/{id}/approve")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<?> approveClinician(@PathVariable Long id) {
        try {
            adminService.approveClinician(id);
            return ResponseEntity.ok(Map.of("message", "Clinician approved successfully"));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/{id}/reject")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<?> rejectClinician(@PathVariable Long id) {
        try {
            adminService.rejectClinician(id);
            return ResponseEntity.ok(Map.of("message", "Clinician rejected successfully"));
        } catch (RuntimeException e) {
            return ResponseEntity.badRequest().body(Map.of("error", e.getMessage()));
        }
    }
}
