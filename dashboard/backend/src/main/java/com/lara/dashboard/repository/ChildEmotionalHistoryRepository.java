package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildEmotionalHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

@Repository
public interface ChildEmotionalHistoryRepository extends JpaRepository<ChildEmotionalHistory, Long> {

    List<ChildEmotionalHistory> findByChildIdAndRecordedDateBetween(Long childId, LocalDate from, LocalDate to);

    List<ChildEmotionalHistory> findTop7ByChildIdOrderByRecordedDateDesc(Long childId);
}
