package com.lara.dashboard.repository;

import com.lara.dashboard.model.OverrideLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface OverrideLogRepository extends JpaRepository<OverrideLog, Long> {
    List<OverrideLog> findBySessionId(String sessionId);
}
