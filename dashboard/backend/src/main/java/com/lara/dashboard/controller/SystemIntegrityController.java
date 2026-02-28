package com.lara.dashboard.controller;

import com.lara.dashboard.dto.SystemIntegrityDto;
import com.lara.dashboard.model.OverrideLog;
import com.lara.dashboard.repository.OverrideLogRepository;
import com.lara.dashboard.service.SystemIntegrityService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/system")
@RequiredArgsConstructor
public class SystemIntegrityController {

    private final SystemIntegrityService systemIntegrityService;
    private final OverrideLogRepository overrideLogRepository;

    @GetMapping("/integrity")
    @PreAuthorize("hasAnyRole('RESEARCHER', 'ADMIN')")
    public ResponseEntity<SystemIntegrityDto> getSystemIntegrity() {
        return ResponseEntity.ok(systemIntegrityService.evaluateSystemIntegrity());
    }
    
    @GetMapping("/audit-export")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<OverrideLog>> exportComplianceAuditLog() {
        // Exposes secure endpoint for compliance export of all decisions and overrides.
        // Role is constrained heavily to Admin / Compliance Officer mapping.
        return ResponseEntity.ok(overrideLogRepository.findAll());
    }
}
