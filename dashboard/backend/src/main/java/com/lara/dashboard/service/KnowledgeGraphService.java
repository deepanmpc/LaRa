package com.lara.dashboard.service;

import com.lara.dashboard.model.KnowledgeEdge;
import com.lara.dashboard.model.KnowledgeNode;
import com.lara.dashboard.repository.KnowledgeEdgeRepository;
import com.lara.dashboard.repository.KnowledgeNodeRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Map;

@Service
@RequiredArgsConstructor
@Slf4j
public class KnowledgeGraphService {

    private final KnowledgeNodeRepository nodeRepository;
    private final KnowledgeEdgeRepository edgeRepository;

    public Map<String, Object> getGraphData(String childIdHashed) {
        // Fetch all nodes for the user
        List<KnowledgeNode> nodes = nodeRepository.findByChildIdHashed(childIdHashed);
        
        // In a real application, we would fetch edges strictly tied to these nodes.
        // For scaffold purposes, we return them cleanly.
        // We calculate centrality or format them as `{ "nodes": [...], "links": [...] }`
        // which matches the expected payload for `react-force-graph-3d`.

        // Since EdgeRepository here fetches by Source or Target, we'd iterate
        // or write a custom JPQL query `SELECT e FROM KnowledgeEdge e WHERE e.sourceNodeId IN :nodeIds`

        return Map.of(
                "nodes", nodes,
                "links", List.of() // Mocking the edges mapping for simplicity in scaffold
        );
    }
}
