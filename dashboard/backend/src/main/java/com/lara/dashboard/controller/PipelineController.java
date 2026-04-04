package com.lara.dashboard.controller;

import com.lara.dashboard.dto.SessionCompleteRequest;
import com.lara.dashboard.service.SessionIngestionService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/pipeline")
@RequiredArgsConstructor
@Slf4j
public class PipelineController {

    private final SessionIngestionService ingestionService;

    /**
     * Called by the Python pipeline at session end.
     * Ingests all session data into the MySQL database.
     * No authentication required — internal service-to-service call.
     */
    @PostMapping("/session-complete")
    public ResponseEntity<?> sessionComplete(@RequestBody SessionCompleteRequest request) {
        try {
            Long sessionId = ingestionService.ingestSession(request);
            return ResponseEntity.ok(Map.of(
                    "status", "SUCCESS",
                    "sessionId", sessionId,
                    "message", "Session data ingested successfully"
            ));
        } catch (RuntimeException e) {
            if (e.getMessage() != null && e.getMessage().contains("Duplicate session UUID")) {
                return ResponseEntity.status(HttpStatus.CONFLICT).body(Map.of(
                        "status", "DUPLICATE",
                        "message", e.getMessage()
                ));
            }
            log.error("[Pipeline] Session ingestion failed", e);
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(Map.of(
                    "status", "ERROR",
                    "message", e.getMessage()
            ));
        }
    }
}
