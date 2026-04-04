package com.lara.dashboard.repository;

import com.lara.dashboard.entity.SessionDifficultyTrajectory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SessionDifficultyTrajectoryRepository extends JpaRepository<SessionDifficultyTrajectory, Long> {

    List<SessionDifficultyTrajectory> findBySessionIdOrderByTurnNumberAsc(Long sessionId);
}
