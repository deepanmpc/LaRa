package com.lara.dashboard.repository;

import com.lara.dashboard.model.KnowledgeNode;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface KnowledgeNodeRepository extends JpaRepository<KnowledgeNode, Long> {
    List<KnowledgeNode> findByChildIdHashed(String childIdHashed);
    KnowledgeNode findByChildIdHashedAndNodeId(String childIdHashed, String nodeId);
}
