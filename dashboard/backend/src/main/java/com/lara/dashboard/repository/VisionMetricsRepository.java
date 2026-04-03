package com.lara.dashboard.repository;

import com.lara.dashboard.entity.VisionMetrics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface VisionMetricsRepository extends JpaRepository<VisionMetrics, Long> {
    Optional<VisionMetrics> findBySessionId(Long sessionId);
}
