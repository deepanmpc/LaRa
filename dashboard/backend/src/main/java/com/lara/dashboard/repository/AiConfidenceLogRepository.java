package com.lara.dashboard.repository;

import com.lara.dashboard.model.AiConfidenceLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface AiConfidenceLogRepository extends JpaRepository<AiConfidenceLog, Long> {
    List<AiConfidenceLog> findBySessionId(String sessionId);
    List<AiConfidenceLog> findByChildIdHashed(String childIdHashed);
}
