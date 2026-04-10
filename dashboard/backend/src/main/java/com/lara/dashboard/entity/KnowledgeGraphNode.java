package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "knowledge_graph_nodes")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class KnowledgeGraphNode {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "node_id", nullable = false)
    private String nodeId;

    @Column(name = "label")
    private String label;

    @Column(name = "node_type", nullable = false)
    private String nodeType;

    @Column(name = "child_id_hashed", nullable = false)
    private String childIdHashed;

    @Column(name = "computed_weight")
    private Double computedWeight;
}
