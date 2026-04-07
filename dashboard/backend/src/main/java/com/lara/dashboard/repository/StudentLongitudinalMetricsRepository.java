package com.lara.dashboard.repository;

import com.lara.dashboard.entity.StudentLongitudinalMetrics;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface StudentLongitudinalMetricsRepository extends JpaRepository<StudentLongitudinalMetrics, String> {
    Optional<StudentLongitudinalMetrics> findByStudentId(String studentId);
}
