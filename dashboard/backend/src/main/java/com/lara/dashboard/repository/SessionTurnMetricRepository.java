package com.lara.dashboard.repository;

import com.lara.dashboard.entity.SessionTurnMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SessionTurnMetricRepository extends JpaRepository<SessionTurnMetric, Long> {

    List<SessionTurnMetric> findBySessionIdOrderByTurnNumberAsc(Long sessionId);
}
