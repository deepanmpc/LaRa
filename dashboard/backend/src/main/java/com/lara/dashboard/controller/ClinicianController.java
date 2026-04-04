package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ChildResponse;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.SessionRepository;
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
    private final SessionRepository sessionRepository;
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
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        ClinicianProfile profile = clinicianProfileRepository.findByUserId(user.getId())
                .orElseThrow(() -> new RuntimeException("Clinician profile not found"));

        List<Child> children = childRepository.findByClinicianId(profile.getId());
        
        List<ChildResponse> responses = children.stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());

        return ResponseEntity.ok(responses);
    }

    @GetMapping("/students/{id}")
    @PreAuthorize("hasAuthority('ROLE_CLINICIAN')")
    public ResponseEntity<ChildResponse> getStudentById(@PathVariable Long id, Authentication authentication) {
        String email = authentication.getName();
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        ClinicianProfile profile = clinicianProfileRepository.findByUserId(user.getId())
                .orElseThrow(() -> new RuntimeException("Clinician profile not found"));

        Child child = childRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        // Security check — child must belong to this clinician
        if (child.getClinician() == null || !child.getClinician().getId().equals(profile.getId())) {
            return ResponseEntity.status(org.springframework.http.HttpStatus.FORBIDDEN).build();
        }

        return ResponseEntity.ok(mapToResponse(child));
    }

    @GetMapping("/sessions")
    @PreAuthorize("hasAuthority('ROLE_CLINICIAN')")
    public ResponseEntity<List<com.lara.dashboard.dto.SessionResponse>> getSessions(Authentication authentication) {
        String email = authentication.getName();
        User user = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));
        
        ClinicianProfile profile = clinicianProfileRepository.findByUserId(user.getId())
                .orElseThrow(() -> new RuntimeException("Clinician profile not found"));

        return ResponseEntity.ok(clinicianService.getAllSessions(profile.getId()));
    }

    @GetMapping("/list-clinicians")
    public ResponseEntity<List<Map<String, Object>>> getClinicianList() {
        List<ClinicianProfile> approvedProfiles = clinicianProfileRepository.findByApprovalStatus("APPROVED");
        
        List<Map<String, Object>> responses = approvedProfiles.stream()
                .map(cp -> Map.of(
                    "id", (Object)cp.getId(), 
                    "name", (Object)(cp.getUser() != null ? cp.getUser().getName() : "Unknown")
                ))
                .collect(Collectors.toList());

        return ResponseEntity.ok(responses);
    }

    @GetMapping("/approved")
    @PreAuthorize("hasAnyAuthority('ROLE_FAMILY', 'ROLE_ADMIN', 'ROLE_CLINICIAN')")
    @org.springframework.transaction.annotation.Transactional(readOnly = true)
    public ResponseEntity<List<com.lara.dashboard.dto.ClinicianSummaryDTO>> getApprovedClinicians() {
        // Use a more explicit query to avoid any hidden status filtering
        List<ClinicianProfile> profiles = clinicianProfileRepository.findByApprovalStatus("APPROVED");
        
        System.out.println("DEBUG: Found " + profiles.size() + " approved clinician profiles");

        List<com.lara.dashboard.dto.ClinicianSummaryDTO> result = profiles.stream()
            .map(p -> com.lara.dashboard.dto.ClinicianSummaryDTO.builder()
                .id(p.getId())
                .name(p.getUser() != null ? p.getUser().getName() : "Unknown Clinician")
                .organization(p.getOrganization())
                .specialization(p.getSpecialization())
                .build())
            .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }

    private ChildResponse mapToResponse(Child child) {
        String lastSessionDate = sessionRepository.findTopByChild_IdOrderByEndTimeDesc(child.getId())
                .map(s -> s.getEndTime() != null ? s.getEndTime().format(java.time.format.DateTimeFormatter.ofPattern("MMM dd, yyyy")) : "No sessions yet")
                .orElse("No sessions yet");

        ClinicianProfile cp = child.getClinician();
        return ChildResponse.builder()
                .id(child.getId())
                .name(child.getName())
                .age(child.getAge())
                .gradeLevel(child.getGradeLevel())
                .lastSessionDate(lastSessionDate)
                .clinicianId(cp != null ? cp.getId() : null)
                .clinicianName(cp != null && cp.getUser() != null ? cp.getUser().getName() : null)
                .build();
    }
}
