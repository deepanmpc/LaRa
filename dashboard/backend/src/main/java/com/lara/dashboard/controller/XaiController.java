package com.lara.dashboard.controller;

import com.lara.dashboard.model.AiConfidenceLog;
import com.lara.dashboard.repository.AiConfidenceLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/xai")
@RequiredArgsConstructor
public class XaiController {

    private final AiConfidenceLogRepository aiConfidenceLogRepository;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<List<AiConfidenceLog>> getXaiInsights(
            @PathVariable String userId) {
        
        // Exposing raw XAI logs for the frontend to render Confidence Distribution 
        // and Feature Attribution Bar Charts required by Module 3.
        return ResponseEntity.ok(aiConfidenceLogRepository.findByChildIdHashed(userId));
    }
}
