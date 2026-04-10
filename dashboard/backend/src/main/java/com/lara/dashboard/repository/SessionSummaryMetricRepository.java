package com.lara.dashboard.repository;

import com.lara.dashboard.entity.SessionSummaryMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.Optional;

@Repository
public interface SessionSummaryMetricRepository extends JpaRepository<SessionSummaryMetric, Long> {
    Optional<SessionSummaryMetric> findByChildIdHashedAndSummaryDate(String childIdHashed, LocalDate summaryDate);
}
