package com.lara.dashboard.repository;

import com.lara.dashboard.entity.KnowledgeGraphNode;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface KnowledgeGraphNodeRepository extends JpaRepository<KnowledgeGraphNode, Long> {
    List<KnowledgeGraphNode> findByChildIdHashed(String childIdHashed);
}
