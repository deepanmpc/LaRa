package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildLearningProgress;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChildLearningProgressRepository extends JpaRepository<ChildLearningProgress, Long> {

    List<ChildLearningProgress> findByChildId(Long childId);

    Optional<ChildLearningProgress> findByChildIdAndConceptName(Long childId, String conceptName);

    List<ChildLearningProgress> findByChildIdAndMasteryStatus(Long childId, String status);
}
