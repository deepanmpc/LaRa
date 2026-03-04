package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ClinicianProfile;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ClinicianProfileRepository extends JpaRepository<ClinicianProfile, Long> {
    Optional<ClinicianProfile> findByUserId(Long userId);
}
