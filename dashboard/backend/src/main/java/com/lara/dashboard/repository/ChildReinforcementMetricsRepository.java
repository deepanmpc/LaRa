package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildReinforcementMetrics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChildReinforcementMetricsRepository extends JpaRepository<ChildReinforcementMetrics, Long> {

    List<ChildReinforcementMetrics> findByChildId(Long childId);

    Optional<ChildReinforcementMetrics> findByChildIdAndStyleName(Long childId, String styleName);
}
