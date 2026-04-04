package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.enums.UserStatus;
import org.springframework.data.jpa.repository.EntityGraph;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface ClinicianProfileRepository extends JpaRepository<ClinicianProfile, Long> {

    @EntityGraph(attributePaths = {"user"})
    Optional<ClinicianProfile> findByUserId(Long userId);

    List<ClinicianProfile> findAllByUser_Status(UserStatus status);

    @EntityGraph(attributePaths = {"user"})
    List<ClinicianProfile> findByApprovalStatus(String status);
}
