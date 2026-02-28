package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ToolEffectivenessDto;
import com.lara.dashboard.service.ToolEffectivenessDecayService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/tool-effectiveness")
@RequiredArgsConstructor
public class ToolEffectivenessController {

    private final ToolEffectivenessDecayService effectivenessService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<ToolEffectivenessDto> getEffectivenessDecay(@PathVariable String userId) {
        return ResponseEntity.ok(effectivenessService.computeDecayMetrics(userId));
    }
}
