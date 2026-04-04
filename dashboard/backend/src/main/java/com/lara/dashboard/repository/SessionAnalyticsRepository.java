package com.lara.dashboard.repository;

import com.lara.dashboard.entity.SessionAnalytics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface SessionAnalyticsRepository extends JpaRepository<SessionAnalytics, Long> {

    Optional<SessionAnalytics> findBySessionId(Long sessionId);

    List<SessionAnalytics> findByChildIdOrderByCreatedAtDesc(Long childId);

    List<SessionAnalytics> findTop7ByChildIdOrderByCreatedAtDesc(Long childId);

    Optional<SessionAnalytics> findTopByChildIdOrderByCreatedAtDesc(Long childId);

    @org.springframework.data.jpa.repository.Modifying
    @org.springframework.data.jpa.repository.Query("DELETE FROM SessionAnalytics s WHERE s.session.id = :sessionId")
    void deleteBySessionId(@org.springframework.data.repository.query.Param("sessionId") Long sessionId);
}
