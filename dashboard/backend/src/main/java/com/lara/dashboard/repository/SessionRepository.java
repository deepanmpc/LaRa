package com.lara.dashboard.repository;

import com.lara.dashboard.entity.Session;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface SessionRepository extends JpaRepository<Session, Long> {
    Optional<Session> findBySessionId(String sessionId);
    java.util.List<Session> findAllByChild_Id(Long childId);
}
