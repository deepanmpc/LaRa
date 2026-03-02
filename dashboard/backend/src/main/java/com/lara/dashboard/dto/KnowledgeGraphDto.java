package com.lara.dashboard.dto;

import lombok.Builder;
import lombok.Data;

import java.util.List;

@Data
@Builder
public class KnowledgeGraphDto {

    private List<GraphNode> nodes;
    private List<GraphLink> links;

    @Data
    @Builder
    public static class GraphNode {
        private String id;
        private Integer group;
        private String label;
        private Integer val;
    }

    @Data
    @Builder
    public static class GraphLink {
        private String source;
        private String target;
        private Double strength;
        private String type;
        private String color;
    }
}
