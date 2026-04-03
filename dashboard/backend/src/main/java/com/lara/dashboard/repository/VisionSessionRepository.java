package com.lara.dashboard.repository;

import com.lara.dashboard.entity.VisionSession;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface VisionSessionRepository extends JpaRepository<VisionSession, Long> {
    List<VisionSession> findByChildIdOrderByStartedAtDesc(Long childId);
    Optional<VisionSession> findFirstByChildIdOrderByStartedAtDesc(Long childId);
}
