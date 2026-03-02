package com.lara.dashboard.controller;

import com.lara.dashboard.dto.simple.SimpleDashboardResponseDTO;
import com.lara.dashboard.service.SimpleDashboardService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Optional;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
@CrossOrigin(origins = "http://localhost:5173")
public class SimpleDashboardController {

    private final SimpleDashboardService simpleDashboardService;

    @GetMapping("/simple/{studentId}")
    public ResponseEntity<SimpleDashboardResponseDTO> getSimpleDashboard(@PathVariable String studentId) {
        if (studentId == null || studentId.trim().isEmpty()) {
            return ResponseEntity.badRequest().build();
        }

        Optional<SimpleDashboardResponseDTO> responseOpt = simpleDashboardService.getDashboardData(studentId);
        
        return responseOpt.map(ResponseEntity::ok)
                .orElseGet(() -> ResponseEntity.notFound().build());
    }
}
