package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildVisionMetricsEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChildVisionMetricsEntityRepository extends JpaRepository<ChildVisionMetricsEntity, Long> {

    List<ChildVisionMetricsEntity> findByChildIdOrderByRecordedAtDesc(Long childId);

    Optional<ChildVisionMetricsEntity> findTopByChildIdOrderByRecordedAtDesc(Long childId);
    Optional<ChildVisionMetricsEntity> findBySessionId(Long sessionId);
}
