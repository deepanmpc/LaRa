package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ToolIntervention;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ToolInterventionRepository extends JpaRepository<ToolIntervention, Long> {

    List<ToolIntervention> findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(
        String childIdHashed,
        LocalDateTime timestamp
    );

    Long countByChildIdHashedAndTimestampAfter(String childIdHashed, LocalDateTime after);
    java.util.Optional<ToolIntervention> findTopByChildIdHashedOrderByTimestampDesc(String childIdHashed);
}
