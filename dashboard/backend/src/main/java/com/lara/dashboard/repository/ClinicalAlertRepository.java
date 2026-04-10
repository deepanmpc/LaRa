package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ClinicalAlert;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ClinicalAlertRepository extends JpaRepository<ClinicalAlert, Long> {
    List<ClinicalAlert> findByChildIdAndResolvedOrderByCreatedAtDesc(Long childId, boolean resolved);
    List<ClinicalAlert> findBySeverityAndResolved(String severity, boolean resolved);
}
