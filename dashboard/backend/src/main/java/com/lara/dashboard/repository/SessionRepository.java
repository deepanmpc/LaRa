package com.lara.dashboard.repository;

import com.lara.dashboard.entity.Session;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface SessionRepository extends JpaRepository<Session, Long> {
    Optional<Session> findBySessionId(String sessionId);
    java.util.List<Session> findAllByChild_Id(Long childId);
    java.util.List<Session> findByChild_Clinician_Id(Long clinicianId);

    @org.springframework.data.jpa.repository.Query("SELECT SUM(s.durationSeconds) FROM Session s WHERE s.child.id = :childId AND s.startTime >= :after")
    Long sumDurationByChildIdAndStartTimeAfter(@org.springframework.data.repository.query.Param("childId") Long childId, @org.springframework.data.repository.query.Param("after") java.time.LocalDateTime after);

    @org.springframework.data.jpa.repository.Query("SELECT AVG(s.durationSeconds) FROM Session s WHERE s.child.id = :childId")
    Double avgDurationByChildId(@org.springframework.data.repository.query.Param("childId") Long childId);

    Long countByChild_IdAndStartTimeAfter(Long childId, java.time.LocalDateTime after);
    Long countByChild_Id(Long childId);
    Optional<Session> findTopByChild_IdOrderByEndTimeDesc(Long childId);
    java.util.List<Session> findByChild_IdAndStartTimeBetween(Long childId, java.time.LocalDateTime from, java.time.LocalDateTime to);
}
