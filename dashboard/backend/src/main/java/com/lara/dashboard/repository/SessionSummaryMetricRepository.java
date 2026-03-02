package com.lara.dashboard.repository;

import com.lara.dashboard.model.SessionSummaryMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface SessionSummaryMetricRepository extends JpaRepository<SessionSummaryMetric, Long> {
    List<SessionSummaryMetric> findByChildIdHashedAndSummaryDateBetweenOrderBySummaryDateAsc(String childIdHashed, LocalDate start, LocalDate end);
    Optional<SessionSummaryMetric> findByChildIdHashedAndSummaryDate(String childIdHashed, LocalDate summaryDate);
}
