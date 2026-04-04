package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildEngagementHistory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChildEngagementHistoryRepository extends JpaRepository<ChildEngagementHistory, Long> {

    List<ChildEngagementHistory> findTop7ByChildIdOrderByRecordedDateDesc(Long childId);
}
