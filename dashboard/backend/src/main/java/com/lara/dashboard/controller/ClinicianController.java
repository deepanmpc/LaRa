package com.lara.dashboard.controller;

import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.Map;
import java.util.Optional;

@RestController
@RequestMapping("/api/clinician")
@RequiredArgsConstructor
public class ClinicianController {

    private final UserRepository userRepository;
    private final ClinicianProfileRepository clinicianProfileRepository;

    @GetMapping("/status")
    public ResponseEntity<?> getStatus(Authentication authentication) {
        String email = authentication.getName();
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Optional<ClinicianProfile> profile = clinicianProfileRepository.findByUserId(user.getId());

        Map<String, Object> statusResponse = Map.of(
                "name", user.getName(),
                "email", user.getEmail(),
                "status", user.getStatus().name(),
                "approvalStatus", profile.map(ClinicianProfile::getApprovalStatus).orElse("PENDING"),
                "message", "PENDING".equals(user.getStatus().name())
                        ? "Your account is awaiting admin approval. You will be notified once reviewed."
                        : "Your account is active."
        );

        return ResponseEntity.ok(statusResponse);
    }
}
