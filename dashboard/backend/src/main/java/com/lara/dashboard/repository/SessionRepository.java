package com.lara.dashboard.repository;

import com.lara.dashboard.model.Session;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface SessionRepository extends JpaRepository<Session, Long> {
    List<Session> findByChildIdHashed(String childIdHashed);
    Session findBySessionId(String sessionId);
}
