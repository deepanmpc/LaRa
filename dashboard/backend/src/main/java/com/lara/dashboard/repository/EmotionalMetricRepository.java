package com.lara.dashboard.repository;

import com.lara.dashboard.model.EmotionalMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface EmotionalMetricRepository extends JpaRepository<EmotionalMetric, Long> {
    List<EmotionalMetric> findByChildIdHashedAndTimestampBetween(String childIdHashed, LocalDateTime start, LocalDateTime end);
    List<EmotionalMetric> findBySessionId(String sessionId);
}
