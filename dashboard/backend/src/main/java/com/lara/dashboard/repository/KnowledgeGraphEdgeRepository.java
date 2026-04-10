package com.lara.dashboard.repository;

import com.lara.dashboard.entity.KnowledgeGraphEdge;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface KnowledgeGraphEdgeRepository extends JpaRepository<KnowledgeGraphEdge, Long> {
    
    @Query("SELECT e FROM KnowledgeGraphEdge e WHERE e.sourceNodeId IN :nodeIds OR e.targetNodeId IN :nodeIds")
    List<KnowledgeGraphEdge> findEdgesForNodes(@Param("nodeIds") List<Long> nodeIds);
}
