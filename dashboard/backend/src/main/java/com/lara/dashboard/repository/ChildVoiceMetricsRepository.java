package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildVoiceMetrics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChildVoiceMetricsRepository extends JpaRepository<ChildVoiceMetrics, Long> {

    List<ChildVoiceMetrics> findByChildIdOrderByRecordedAtDesc(Long childId);

    Optional<ChildVoiceMetrics> findTopByChildIdOrderByRecordedAtDesc(Long childId);
}
