package com.lara.dashboard.repository;

import com.lara.dashboard.entity.EngagementTimeline;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface EngagementTimelineRepository extends JpaRepository<EngagementTimeline, Long> {
    List<EngagementTimeline> findBySessionIdOrderByMinuteIndexAsc(Long sessionId);
}
