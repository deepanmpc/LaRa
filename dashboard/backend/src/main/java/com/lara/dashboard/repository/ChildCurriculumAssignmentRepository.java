package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildCurriculumAssignment;
import com.lara.dashboard.enums.CurriculumAssignmentStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ChildCurriculumAssignmentRepository extends JpaRepository<ChildCurriculumAssignment, Long> {

    List<ChildCurriculumAssignment> findByChildId(Long childId);

    List<ChildCurriculumAssignment> findByChildIdAndStatus(Long childId, CurriculumAssignmentStatus status);
}
