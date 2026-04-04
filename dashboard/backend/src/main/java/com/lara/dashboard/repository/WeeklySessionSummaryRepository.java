package com.lara.dashboard.repository;

import com.lara.dashboard.entity.WeeklySessionSummary;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

@Repository
public interface WeeklySessionSummaryRepository extends JpaRepository<WeeklySessionSummary, Long> {

    Optional<WeeklySessionSummary> findByChildIdAndWeekStartDate(Long childId, LocalDate weekStart);

    List<WeeklySessionSummary> findTop4ByChildIdOrderByWeekStartDateDesc(Long childId);
}
