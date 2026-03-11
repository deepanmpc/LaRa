package com.lara.dashboard.service;

import com.lara.dashboard.dto.ClinicianResponse;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.enums.UserStatus;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class AdminService {

    private final UserRepository userRepository;
    private final ClinicianProfileRepository clinicianProfileRepository;

    @Transactional(readOnly = true)
    public List<ClinicianResponse> getPendingClinicians() {
        return clinicianProfileRepository.findAllByUserStatus(UserStatus.PENDING)
                .stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());
    }

    @Transactional
    public void approveClinician(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));
        
        user.setStatus(UserStatus.APPROVED);
        userRepository.save(user);

        // Upsert: create profile if it somehow doesn't exist (e.g. old test accounts)
        ClinicianProfile profile = clinicianProfileRepository.findByUserId(userId)
                .orElseGet(() -> ClinicianProfile.builder().user(user).build());
        profile.setApprovalStatus("APPROVED");
        clinicianProfileRepository.save(profile);
    }

    @Transactional
    public void rejectClinician(Long userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new RuntimeException("User not found"));

        user.setStatus(UserStatus.REJECTED);
        userRepository.save(user);

        // Upsert: create profile if it somehow doesn't exist (e.g. old test accounts)
        ClinicianProfile profile = clinicianProfileRepository.findByUserId(userId)
                .orElseGet(() -> ClinicianProfile.builder().user(user).build());
        profile.setApprovalStatus("REJECTED");
        clinicianProfileRepository.save(profile);
    }

    private ClinicianResponse mapToResponse(ClinicianProfile profile) {
        User user = profile.getUser();
        return ClinicianResponse.builder()
                .id(user.getId())
                .name(user.getName())
                .email(user.getEmail())
                .phone(profile.getPhone())
                .organization(profile.getOrganization())
                .specialization(profile.getSpecialization())
                .licenseNumber(profile.getLicenseNumber())
                .yearsOfExperience(profile.getYearsOfExperience())
                .status(user.getStatus().name())
                .createdAt(user.getCreatedAt())
                .build();
    }
}
