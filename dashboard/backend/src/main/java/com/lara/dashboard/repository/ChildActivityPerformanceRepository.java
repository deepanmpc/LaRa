package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildActivityPerformance;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChildActivityPerformanceRepository extends JpaRepository<ChildActivityPerformance, Long> {

    List<ChildActivityPerformance> findByChildIdOrderByAvgScoreDesc(Long childId);

    Optional<ChildActivityPerformance> findByChildIdAndActivityName(Long childId, String activityName);
}
