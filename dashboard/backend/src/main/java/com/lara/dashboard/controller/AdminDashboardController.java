package com.lara.dashboard.controller;

import com.lara.dashboard.entity.*;
import com.lara.dashboard.repository.*;
import com.lara.dashboard.service.*;
import com.lara.dashboard.jobs.MetricsCompactionJob;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.*;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/admin")
@RequiredArgsConstructor
public class AdminDashboardController {

    private final AdminService adminService;
    private final SessionTurnMetricRepository turnMetricRepository;
    private final ClinicalAlertRepository clinicalAlertRepository;
    private final ModelEvaluationService modelEvaluationService;
    private final DatasetExportService datasetExportService;
    private final PopulationAnalyticsService populationAnalyticsService;
    private final MetricsCompactionJob metricsCompactionJob;
    private final UserRepository userRepository;

    // PART 2 — System Monitoring APIs
    @GetMapping("/system/metrics")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getSystemMetrics() {
        Map<String, Object> metrics = new LinkedHashMap<>();
        
        // Compute average latencies from last 100 turns
        List<SessionTurnMetric> recentTurns = turnMetricRepository.findAll().stream()
                .sorted(Comparator.comparing(SessionTurnMetric::getId).reversed())
                .limit(100)
                .collect(Collectors.toList());

        metrics.put("runtime_latency_ms", recentTurns.stream().mapToLong(t -> t.getTotalLatencyMs() != null ? t.getTotalLatencyMs() : 0).average().orElse(0));
        metrics.put("llm_inference_time_ms", recentTurns.stream().mapToLong(t -> t.getInferenceMs() != null ? t.getInferenceMs() : 0).average().orElse(0));
        metrics.put("tts_latency_ms", recentTurns.stream().mapToLong(t -> t.getTtsMs() != null ? t.getTtsMs() : 0).average().orElse(0));
        metrics.put("db_write_latency_ms", 12); // Simulated
        metrics.put("event_bus_queue_size", 0); // Simulated
        metrics.put("active_sessions", adminService.getSystemMetrics().get("activeSessions"));
        metrics.put("alerts_last_24h", clinicalAlertRepository.findAll().stream()
                .filter(a -> a.getCreatedAt().isAfter(LocalDateTime.now().minusDays(1)))
                .count());

        return ResponseEntity.ok(metrics);
    }

    // PART 3 — Model Evaluation APIs
    @GetMapping("/model/evaluation")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getModelEvaluation() {
        return ResponseEntity.ok(modelEvaluationService.getModelEvaluation());
    }

    // PART 4 — Dataset Export
    @GetMapping("/export-dataset")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<String> exportDataset() {
        String csv = datasetExportService.exportToCsv();
        return ResponseEntity.ok()
                .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=lara_dataset.csv")
                .contentType(MediaType.parseMediaType("text/csv"))
                .body(csv);
    }

    // PART 5 — Population Analytics
    @GetMapping("/population/analytics")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getPopulationAnalytics() {
        return ResponseEntity.ok(populationAnalyticsService.getPopulationAnalytics());
    }

    // PART 6 — Metrics Compaction Status
    @GetMapping("/system/compaction-status")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Map<String, Object>> getCompactionStatus() {
        return ResponseEntity.ok(metricsCompactionJob.getStatus());
    }

    // PART 7 — Alert Monitoring
    @GetMapping("/alerts")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<List<ClinicalAlert>> getAlerts(
            @RequestParam(required = false) String severity,
            @RequestParam(required = false) Boolean resolved) {
        
        return ResponseEntity.ok(clinicalAlertRepository.findAll().stream()
                .filter(a -> severity == null || a.getSeverity().equalsIgnoreCase(severity))
                .filter(a -> resolved == null || a.getResolved().equals(resolved))
                .sorted(Comparator.comparing(ClinicalAlert::getCreatedAt).reversed())
                .collect(Collectors.toList()));
    }

    @PostMapping("/alerts/{id}/resolve")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Void> resolveAlert(@PathVariable Long id) {
        clinicalAlertRepository.findById(id).ifPresent(a -> {
            a.setResolved(true);
            clinicalAlertRepository.save(a);
        });
        return ResponseEntity.ok().build();
    }

    // PART 8 — User Management
    @GetMapping("/users")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<List<User>> getAllUsers() {
        return ResponseEntity.ok(userRepository.findAll());
    }

    @PostMapping("/users/{id}/approve")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Void> approveUser(@PathVariable Long id) {
        adminService.approveClinician(id);
        return ResponseEntity.ok().build();
    }

    @PostMapping("/users/{id}/suspend")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Void> suspendUser(@PathVariable Long id) {
        userRepository.findById(id).ifPresent(u -> {
            u.setStatus(com.lara.dashboard.enums.UserStatus.REJECTED); // Mapping REJECTED as suspended for now
            userRepository.save(u);
        });
        return ResponseEntity.ok().build();
    }

    @DeleteMapping("/users/{id}")
    @PreAuthorize("hasAuthority('ROLE_ADMIN')")
    public ResponseEntity<Void> deleteUser(@PathVariable Long id) {
        userRepository.deleteById(id);
        return ResponseEntity.ok().build();
    }
}
