package com.lara.dashboard.controller;

import com.lara.dashboard.service.KnowledgeGraphService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api/graph")
@RequiredArgsConstructor
public class GraphController {

    private final KnowledgeGraphService knowledgeGraphService;

    @GetMapping("/{userId}")
    @PreAuthorize("hasAnyRole('CLINICIAN', 'RESEARCHER', 'ADMIN')")
    public ResponseEntity<Map<String, Object>> getKnowledgeGraph(@PathVariable String userId) {
        return ResponseEntity.ok(knowledgeGraphService.getGraphData(userId));
    }
}
