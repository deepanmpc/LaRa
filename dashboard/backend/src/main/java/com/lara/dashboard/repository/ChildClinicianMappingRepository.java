package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ChildClinicianMapping;
import com.lara.dashboard.enums.MappingStatus;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ChildClinicianMappingRepository extends JpaRepository<ChildClinicianMapping, Long> {

    List<ChildClinicianMapping> findByClinicianId(Long clinicianId);

    List<ChildClinicianMapping> findByChildId(Long childId);

    Optional<ChildClinicianMapping> findByChildIdAndClinicianIdAndStatus(Long childId, Long clinicianId, MappingStatus status);

    Optional<ChildClinicianMapping> findByChildIdAndClinicianId(Long childId, Long clinicianId);

    boolean existsByChildIdAndClinicianId(Long childId, Long clinicianId);

    List<ChildClinicianMapping> findByClinicianIdAndStatus(Long clinicianId, MappingStatus status);
}
