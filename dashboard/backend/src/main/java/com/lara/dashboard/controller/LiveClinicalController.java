package com.lara.dashboard.controller;

import com.lara.dashboard.dto.tier2.SessionLiveMetrics;
import com.lara.dashboard.service.AuditLoggingService;
import com.lara.dashboard.service.LiveSessionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/dashboard/clinical/live")
@RequiredArgsConstructor
@Slf4j
@CrossOrigin(origins = "http://localhost:5173")
public class LiveClinicalController {

    private final LiveSessionService liveSessionService;
    private final AuditLoggingService auditLoggingService;

    /**
     * Part 1: LIVE SESSION ANALYTICS.
     * Guaranteed sub-100ms response. Never hits PostgreSQL.
     * Only visible to ROLE_CLINICIAN.
     */
    @GetMapping("/{sessionId}")
    @PreAuthorize("hasRole('CLINICIAN')")
    public ResponseEntity<SessionLiveMetrics> getLiveMetrics(@PathVariable String sessionId) {
        
        Authentication auth = SecurityContextHolder.getContext().getAuthentication();
        String clinicianId = (auth != null) ? auth.getName() : "UNKNOWN";
        
        // Log access per Part 5 constraints
        auditLoggingService.logClinicalAccess(clinicianId, sessionId, "LIVE_HUD_ACCESS");

        long start = System.currentTimeMillis();
        SessionLiveMetrics metrics = liveSessionService.getLiveMetrics(sessionId);
        long duration = System.currentTimeMillis() - start;

        // Dev enforcement check
        if (duration > 100) {
            log.warn("PERFORMANCE BREACH: Live clinical endpoint took {}ms for session {}", duration, sessionId);
        }

        return ResponseEntity.ok(metrics);
    }
}
