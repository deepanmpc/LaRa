package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ChildResponse;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;
import java.util.Optional;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/clinician")
@RequiredArgsConstructor
public class ClinicianController {

    private final UserRepository userRepository;
    private final ClinicianProfileRepository clinicianProfileRepository;
    private final ChildRepository childRepository;
    private final com.lara.dashboard.service.ClinicianService clinicianService;

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

    @GetMapping("/students")
    @PreAuthorize("hasAuthority('ROLE_CLINICIAN')")
    public ResponseEntity<List<ChildResponse>> getAllStudents(Authentication authentication) {
        String email = authentication.getName();
        User clinician = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        List<Child> children = childRepository.findByClinicianUserId(clinician.getId());
        
        List<ChildResponse> responses = children.stream()
                .map(child -> ChildResponse.builder()
                        .id(child.getId())
                        .name(child.getName())
                        .age(child.getAge())
                        .gradeLevel(child.getGradeLevel())
                        .lastSessionDate("Unknown") // Mock fallback
                        .build())
                .collect(Collectors.toList());

        return ResponseEntity.ok(responses);
    }

    @GetMapping("/students/{id}")
    @PreAuthorize("hasAuthority('ROLE_CLINICIAN')")
    public ResponseEntity<ChildResponse> getStudentById(@PathVariable Long id, Authentication authentication) {
        String email = authentication.getName();
        User clinician = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Child child = childRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        // Access check
        if (child.getClinician() == null || !child.getClinician().getUser().getId().equals(clinician.getId())) {
            throw new RuntimeException("Unauthorized: This student is not assigned to you.");
        }

        ChildResponse response = ChildResponse.builder()
                .id(child.getId())
                .name(child.getName())
                .age(child.getAge())
                .gradeLevel(child.getGradeLevel())
                .lastSessionDate("Unknown")
                .build();

        return ResponseEntity.ok(response);
    }
    @GetMapping("/sessions")
    @PreAuthorize("hasAuthority('ROLE_CLINICIAN')")
    public ResponseEntity<List<com.lara.dashboard.dto.SessionResponse>> getSessions(Authentication authentication) {
        String email = authentication.getName();
        User clinician = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
        return ResponseEntity.ok(clinicianService.getAllSessions(clinician.getId()));
    }

    @GetMapping("/list-clinicians")
    public ResponseEntity<List<Map<String, Object>>> getClinicianList() {
        // Find by approvalStatus column in clinician_profiles table
        List<ClinicianProfile> approvedProfiles = clinicianProfileRepository.findByApprovalStatus("APPROVED");
        
        List<Map<String, Object>> responses = approvedProfiles.stream()
                .map(cp -> Map.of(
                    "id", (Object)cp.getUser().getId(), 
                    "name", (Object)cp.getUser().getName()
                ))
                .collect(Collectors.toList());

        return ResponseEntity.ok(responses);
    }
}
