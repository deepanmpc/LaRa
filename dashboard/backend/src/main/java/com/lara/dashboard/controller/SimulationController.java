package com.lara.dashboard.controller;

import com.lara.dashboard.dto.SimulationRequestDto;
import com.lara.dashboard.dto.SimulationResultDto;
import com.lara.dashboard.service.SimulationService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/simulate")
@RequiredArgsConstructor
public class SimulationController {

    private final SimulationService simulationService;

    @PostMapping("/{userId}")
    @PreAuthorize("hasAnyRole('RESEARCHER', 'ADMIN')")
    public ResponseEntity<SimulationResultDto> runSimulation(
            @PathVariable String userId,
            @RequestBody SimulationRequestDto request) {
        // Counterfactual sandbox bound strictly to analytical roles due to clinical risk
        return ResponseEntity.ok(simulationService.runCounterfactualSimulation(userId, request));
    }
}
