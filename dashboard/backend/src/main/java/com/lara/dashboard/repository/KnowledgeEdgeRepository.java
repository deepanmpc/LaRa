package com.lara.dashboard.repository;

import com.lara.dashboard.model.KnowledgeEdge;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface KnowledgeEdgeRepository extends JpaRepository<KnowledgeEdge, Long> {
    List<KnowledgeEdge> findBySourceNodeIdOrTargetNodeId(Long sourceNodeId, Long targetNodeId);
}
