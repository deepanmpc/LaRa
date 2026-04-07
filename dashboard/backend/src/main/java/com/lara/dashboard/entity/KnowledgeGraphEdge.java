package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "knowledge_graph_edges")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class KnowledgeGraphEdge {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "source_node_id", nullable = false)
    private Long sourceNodeId;

    @Column(name = "target_node_id", nullable = false)
    private Long targetNodeId;

    @Column(name = "relationship_type", nullable = false)
    private String relationshipType;

    @Column(name = "weight")
    private Double weight;
}
