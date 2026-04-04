package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ChildRequest;
import com.lara.dashboard.dto.ChildResponse;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.UserRepository;
import com.lara.dashboard.service.ActivityLogService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

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
    private final ActivityLogService activityLogService;

    @GetMapping("/clinicians")
    public ResponseEntity<List<Map<String, Object>>> getClinicianList() {
        // Fetch approved clinicians from profiles table
        return ResponseEntity.ok(clinicianProfileRepository.findByApprovalStatus("APPROVED").stream()
                .filter(cp -> cp.getUser() != null)
                .map(cp -> Map.of(
                        "id", (Object) cp.getUser().getId(),
                        "name", (Object) cp.getUser().getName(),
                        "organization", (Object) cp.getOrganization()
                ))
                .collect(Collectors.toList()));
    }

    @PostMapping
    public ResponseEntity<ChildResponse> createChild(@RequestBody ChildRequest request, Authentication authentication) {
        String email = authentication.getName();
        User parent = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        User clinician = null;
        if (request.getClinicianId() != null) {
            clinician = userRepository.findById(request.getClinicianId()).orElse(null);
        }

        Child child = Child.builder()
                .name(request.getName())
                .age(request.getAge())
                .gradeLevel(request.getGradeLevel())
                .parent(parent)
                .clinician(clinician)
                .build();

        Child savedChild = childRepository.save(child);

        activityLogService.log("New child profile created: " + child.getName() + " by " + parent.getName());

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
    public ResponseEntity<?> deleteChild(@PathVariable Long id, Authentication authentication) {
        String email = authentication.getName();
        User parent = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Child child = childRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        if (!child.getParent().getId().equals(parent.getId())) {
            return ResponseEntity.status(403).body("Unauthorized to delete this child");
        }

        childRepository.delete(child);
        activityLogService.log("Child profile deleted: " + child.getName() + " by " + parent.getName());
        return ResponseEntity.ok().build();
    }

    private ChildResponse mapToResponse(Child child) {
        return ChildResponse.builder()
                .id(child.getId())
                .name(child.getName())
                .age(child.getAge())
                .gradeLevel(child.getGradeLevel())
                .lastSessionDate("Never") // Fallback
                .clinicianId(child.getClinician() != null ? child.getClinician().getId() : null)
                .clinicianName(child.getClinician() != null ? child.getClinician().getName() : "None Assigned")
                .build();
    }
}
