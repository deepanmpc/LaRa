package com.lara.dashboard.service;

import com.lara.dashboard.entity.KnowledgeGraphEdge;
import com.lara.dashboard.entity.KnowledgeGraphNode;
import com.lara.dashboard.repository.KnowledgeGraphEdgeRepository;
import com.lara.dashboard.repository.KnowledgeGraphNodeRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.security.MessageDigest;
import java.util.*;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class KnowledgeGraphService {

    private final KnowledgeGraphNodeRepository nodeRepository;
    private final KnowledgeGraphEdgeRepository edgeRepository;

    public Map<String, Object> getKnowledgeGraph(Long childId) {
        String childIdHashed = hashChildId(childId);
        List<KnowledgeGraphNode> nodes = nodeRepository.findByChildIdHashed(childIdHashed);
        
        if (nodes.isEmpty()) {
            return Map.of("nodes", Collections.emptyList(), "edges", Collections.emptyList());
        }

        List<Long> nodeIds = nodes.stream().map(KnowledgeGraphNode::getId).collect(Collectors.toList());
        List<KnowledgeGraphEdge> edges = edgeRepository.findEdgesForNodes(nodeIds);

        // Step 7 — Graph Insights: Compute blocked concepts
        Set<String> blockedNodeIds = new HashSet<>();
        Map<Long, KnowledgeGraphNode> nodeMap = nodes.stream()
                .collect(Collectors.toMap(KnowledgeGraphNode::getId, n -> n));

        for (KnowledgeGraphEdge edge : edges) {
            if ("prerequisite".equalsIgnoreCase(edge.getRelationshipType())) {
                KnowledgeGraphNode source = nodeMap.get(edge.getSourceNodeId());
                KnowledgeGraphNode target = nodeMap.get(edge.getTargetNodeId());
                
                if (source != null && target != null) {
                    double sourceMastery = source.getComputedWeight() != null ? source.getComputedWeight() : 0.0;
                    if (sourceMastery < 0.4) {
                        blockedNodeIds.add(target.getNodeId());
                    }
                }
            }
        }

        List<Map<String, Object>> nodeData = nodes.stream().map(n -> {
            Map<String, Object> m = new LinkedHashMap<>();
            m.put("id", n.getNodeId());
            m.put("label", n.getLabel());
            m.put("type", n.getNodeType());
            m.put("mastery", n.getComputedWeight() != null ? n.getComputedWeight() : 0.0);
            m.put("isBlocked", blockedNodeIds.contains(n.getNodeId()));
            return m;
        }).collect(Collectors.toList());

        List<Map<String, Object>> edgeData = edges.stream().map(e -> {
            Map<String, Object> m = new LinkedHashMap<>();
            KnowledgeGraphNode source = nodeMap.get(e.getSourceNodeId());
            KnowledgeGraphNode target = nodeMap.get(e.getTargetNodeId());
            if (source == null || target == null) return null;
            
            m.put("source", source.getNodeId());
            m.put("target", target.getNodeId());
            m.put("type", e.getRelationshipType());
            m.put("weight", e.getWeight());
            return m;
        }).filter(Objects::nonNull).collect(Collectors.toList());

        Map<String, Object> graph = new LinkedHashMap<>();
        graph.put("nodes", nodeData);
        graph.put("edges", edgeData);
        graph.put("insights", generateInsights(nodeData));

        return graph;
    }

    private List<String> generateInsights(List<Map<String, Object>> nodes) {
        List<String> insights = new ArrayList<>();
        long blockedCount = nodes.stream().filter(n -> (Boolean) n.get("isBlocked")).count();
        if (blockedCount > 0) {
            insights.add(blockedCount + " concepts are currently blocked by prerequisites.");
        }
        
        Optional<Map<String, Object>> bottleneck = nodes.stream()
                .filter(n -> (double) n.get("mastery") < 0.4)
                .findFirst();
        
        bottleneck.ifPresent(n -> insights.add("Learning bottleneck detected at: " + n.get("label")));
        
        return insights;
    }

    private String hashChildId(Long childId) {
        try {
            MessageDigest md = MessageDigest.getInstance("MD5");
            byte[] array = md.digest(String.valueOf(childId).getBytes());
            StringBuilder sb = new StringBuilder();
            for (int i = 0; i < 8; ++i) { sb.append(Integer.toHexString((array[i] & 0xFF) | 0x100).substring(1,3)); }
            return sb.toString();
        } catch (Exception e) {
            return String.valueOf(childId);
        }
    }
}
