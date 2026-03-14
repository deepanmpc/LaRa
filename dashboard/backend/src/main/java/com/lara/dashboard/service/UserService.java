package com.lara.dashboard.service;

import com.lara.dashboard.dto.ProfileResponse;
import com.lara.dashboard.dto.UpdateProfileRequest;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.enums.Role;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
@RequiredArgsConstructor
public class UserService {

    private final UserRepository userRepository;
    private final ClinicianProfileRepository clinicianProfileRepository;

    public ProfileResponse getProfile(String email) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        return buildProfileResponse(user);
    }

    @Transactional
    public ProfileResponse updateProfile(String email, UpdateProfileRequest request) {
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        user.setName(request.getName());
        user.setEmail(request.getEmail());
        userRepository.save(user);

        if (user.getRole() == Role.ROLE_CLINICIAN) {
            ClinicianProfile profile = clinicianProfileRepository.findByUserId(user.getId())
                    .orElseGet(() -> {
                        // Create a new profile if none exists (shouldn't happen with our Auth logic, but good practice)
                        ClinicianProfile newProfile = new ClinicianProfile();
                        newProfile.setUser(user);
                        return newProfile;
                    });
            
            profile.setOrganization(request.getOrganization());
            profile.setSpecialization(request.getSpecialization());
            clinicianProfileRepository.save(profile);
        }

        return buildProfileResponse(user);
    }

    private ProfileResponse buildProfileResponse(User user) {
        ProfileResponse.ProfileResponseBuilder builder = ProfileResponse.builder()
                .name(user.getName())
                .email(user.getEmail())
                .role(user.getRole().name());

        if (user.getRole() == Role.ROLE_CLINICIAN) {
            clinicianProfileRepository.findByUserId(user.getId()).ifPresent(profile -> {
                builder.organization(profile.getOrganization())
                       .specialization(profile.getSpecialization())
                       .licenseNumber(profile.getLicenseNumber());
            });
        }

        return builder.build();
    }
}
