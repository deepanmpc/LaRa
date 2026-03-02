package com.lara.dashboard.repository;

import com.lara.dashboard.model.StudentLongitudinalMetrics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface StudentLongitudinalMetricsRepository extends JpaRepository<StudentLongitudinalMetrics, String> {
}
