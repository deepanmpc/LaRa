package com.lara.dashboard.repository;

import com.lara.dashboard.entity.EmotionalMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface EmotionalMetricRepository extends JpaRepository<EmotionalMetric, Long> {

    List<EmotionalMetric> findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(
        String childIdHashed,
        LocalDateTime timestamp
    );

    List<EmotionalMetric> findByChildIdHashedAndTimestampAfter(String childIdHashed, LocalDateTime after);

    @org.springframework.data.jpa.repository.Query("SELECT e.primaryEmotion, COUNT(e) FROM EmotionalMetric e WHERE e.childIdHashed = :hash AND e.timestamp > :after GROUP BY e.primaryEmotion ORDER BY COUNT(e) DESC")
    List<Object[]> findEmotionBreakdown(@org.springframework.data.repository.query.Param("hash") String childIdHashed, @org.springframework.data.repository.query.Param("after") LocalDateTime after);
}
