package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ChildRequest;
import com.lara.dashboard.dto.ChildResponse;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.SessionRepository;
import com.lara.dashboard.repository.UserRepository;
import com.lara.dashboard.service.ActivityLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/children")
@RequiredArgsConstructor
public class ChildController {

    private final ChildRepository childRepository;
    private final UserRepository userRepository;
    private final ClinicianProfileRepository clinicianProfileRepository;
    private final SessionRepository sessionRepository;
    private final com.lara.dashboard.repository.VisionSessionRepository visionSessionRepository;
    private final ActivityLogService activityLogService;

    @GetMapping("/clinicians")
    public ResponseEntity<List<Map<String, Object>>> getClinicianList() {
        // Fetch approved clinicians from profiles table
        return ResponseEntity.ok(clinicianProfileRepository.findByApprovalStatus("APPROVED").stream()
                .filter(cp -> cp.getUser() != null)
                .map(cp -> Map.of(
                        "id", (Object) cp.getId(), // Return ClinicianProfile ID
                        "name", (Object) cp.getUser().getName(),
                        "organization", (Object) (cp.getOrganization() != null ? cp.getOrganization() : "")
                ))
                .collect(Collectors.toList()));
    }

    @PostMapping
    public ResponseEntity<ChildResponse> createChild(@RequestBody ChildRequest request, Authentication authentication) {
        String email = authentication.getName();
        User parent = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Child child = Child.builder()
                .name(request.getName())
                .age(request.getAge())
                .gradeLevel(request.getGradeLevel())
                .parent(parent)
                .build();

        if (request.getClinicianId() != null) {
            clinicianProfileRepository.findById(request.getClinicianId()).ifPresent(child::setClinician);
        }

        Child savedChild = childRepository.save(child);

        activityLogService.log("New child profile created: " + child.getName() + " by " + parent.getName() + 
                (request.getClinicianId() != null ? " mapped to clinician ID: " + request.getClinicianId() : ""));

        return ResponseEntity.ok(mapToResponse(savedChild));
    }

    @GetMapping
    public ResponseEntity<List<ChildResponse>> getChildren(Authentication authentication) {
        String email = authentication.getName();
        User parent = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        List<Child> children = childRepository.findByParentId(parent.getId());

        return ResponseEntity.ok(children.stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList()));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ChildResponse> getChild(@PathVariable Long id) {
        Child child = childRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        return ResponseEntity.ok(mapToResponse(child));
    }

    @DeleteMapping("/{id}")
    @org.springframework.transaction.annotation.Transactional
    public ResponseEntity<?> deleteChild(@PathVariable Long id, Authentication authentication) {
        String email = authentication.getName();
        User parent = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Child child = childRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        if (!child.getParent().getId().equals(parent.getId())) {
            return ResponseEntity.status(403).body("Unauthorized to delete this child");
        }

        // Clean up unmapped references manually
        visionSessionRepository.deleteByChildId(child.getId());

        // Delete the child (sessions will be deleted via CascadeType.ALL in Child.java)
        childRepository.delete(child);
        
        activityLogService.log("Child profile deleted: " + child.getName() + " by " + parent.getName());
        return ResponseEntity.ok().build();
    }

    private ChildResponse mapToResponse(Child child) {
        String lastSessionDate = sessionRepository.findTopByChild_IdOrderByEndTimeDesc(child.getId())
                .map(s -> s.getEndTime() != null ? s.getEndTime().format(DateTimeFormatter.ofPattern("MMM dd, yyyy")) : "No sessions yet")
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
                .clinicianOrganization(cp != null ? cp.getOrganization() : null)
                .build();
    }
}
