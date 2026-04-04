package com.lara.dashboard.repository;

import com.lara.dashboard.entity.SessionTurnMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SessionTurnMetricRepository extends JpaRepository<SessionTurnMetric, Long> {

    List<SessionTurnMetric> findBySessionIdOrderByTurnNumberAsc(Long sessionId);
    
    @org.springframework.data.jpa.repository.Modifying
    @org.springframework.data.jpa.repository.Query("DELETE FROM SessionTurnMetric s WHERE s.session.id = :sessionId")
    void deleteBySessionId(@org.springframework.data.repository.query.Param("sessionId") Long sessionId);
}
