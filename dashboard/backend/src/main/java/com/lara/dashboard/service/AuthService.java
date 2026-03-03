package com.lara.dashboard.service;

import com.lara.dashboard.dto.AuthResponse;
import com.lara.dashboard.dto.LoginRequest;
import com.lara.dashboard.dto.RegisterRequest;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.enums.Role;
import com.lara.dashboard.enums.UserStatus;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.UserRepository;
import com.lara.dashboard.security.JwtUtil;
import lombok.RequiredArgsConstructor;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final ClinicianProfileRepository clinicianProfileRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtUtil jwtUtil;

    public AuthResponse register(RegisterRequest request) {
        if (userRepository.existsByEmail(request.getEmail())) {
            throw new RuntimeException("Email already registered");
        }

        Role role;
        try {
            role = Role.valueOf(request.getRole());
        } catch (IllegalArgumentException e) {
            throw new RuntimeException("Invalid role: " + request.getRole());
        }

        // Admin registration is not allowed publicly
        if (role == Role.ROLE_ADMIN) {
            throw new RuntimeException("Cannot self-register as admin");
        }

        UserStatus status = (role == Role.ROLE_FAMILY) ? UserStatus.ACTIVE : UserStatus.PENDING;

        User user = User.builder()
                .name(request.getName())
                .email(request.getEmail())
                .password(passwordEncoder.encode(request.getPassword()))
                .role(role)
                .status(status)
                .build();

        userRepository.save(user);

        // Create clinician profile if needed
        if (role == Role.ROLE_CLINICIAN) {
            ClinicianProfile profile = ClinicianProfile.builder()
                    .user(user)
                    .licenseNumber(request.getLicenseNumber())
                    .specialization(request.getSpecialization())
                    .yearsOfExperience(request.getYearsOfExperience())
                    .approvalStatus("PENDING")
                    .build();
            clinicianProfileRepository.save(profile);
        }

        String token = jwtUtil.generateToken(user.getEmail(), user.getRole().name(), user.getStatus().name());

        return AuthResponse.builder()
                .token(token)
                .role(user.getRole().name())
                .status(user.getStatus().name())
                .userName(user.getName())
                .email(user.getEmail())
                .build();
    }

    public AuthResponse login(LoginRequest request) {
        User user = userRepository.findByEmail(request.getEmail())
                .orElseThrow(() -> new RuntimeException("Invalid email or password"));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new RuntimeException("Invalid email or password");
        }

        String token = jwtUtil.generateToken(user.getEmail(), user.getRole().name(), user.getStatus().name());

        return AuthResponse.builder()
                .token(token)
                .role(user.getRole().name())
                .status(user.getStatus().name())
                .userName(user.getName())
                .email(user.getEmail())
                .build();
    }
}
