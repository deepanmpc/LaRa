package com.lara.dashboard.repository;

import com.lara.dashboard.model.ToolIntervention;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ToolInterventionRepository extends JpaRepository<ToolIntervention, Long> {
    List<ToolIntervention> findByChildIdHashedAndTimestampBetween(String childIdHashed, LocalDateTime start, LocalDateTime end);
}
