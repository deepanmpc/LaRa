package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ChildRequest;
import com.lara.dashboard.dto.ChildResponse;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.ChildClinicianMapping;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.enums.MappingStatus;
import com.lara.dashboard.repository.*;
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
    private final ChildClinicianMappingRepository clinicianMappingRepository;
    private final ActivityLogService activityLogService;

    @GetMapping("/clinicians")
    public ResponseEntity<List<Map<String, Object>>> getClinicianList() {
        return ResponseEntity.ok(clinicianProfileRepository.findByApprovalStatus("APPROVED").stream()
                .filter(cp -> cp.getUser() != null)
                .map(cp -> Map.of(
                        "id", (Object) cp.getId(),
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
                .diagnosis(request.getDiagnosis())
                .notes(request.getNotes())
                .avatarColor(request.getAvatarColor())
                .weeklySessionGoal(request.getWeeklySessionGoal() != null ? request.getWeeklySessionGoal() : 5)
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

    @PutMapping("/{id}")
    public ResponseEntity<ChildResponse> updateChild(@PathVariable Long id, @RequestBody ChildRequest request, Authentication authentication) {
        String email = authentication.getName();
        User parent = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Child child = childRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        if (!child.getParent().getId().equals(parent.getId())) {
            return ResponseEntity.status(403).build();
        }

        if (request.getName() != null) child.setName(request.getName());
        if (request.getAge() != null) child.setAge(request.getAge());
        if (request.getGradeLevel() != null) child.setGradeLevel(request.getGradeLevel());
        if (request.getDiagnosis() != null) child.setDiagnosis(request.getDiagnosis());
        if (request.getNotes() != null) child.setNotes(request.getNotes());
        if (request.getAvatarColor() != null) child.setAvatarColor(request.getAvatarColor());
        if (request.getWeeklySessionGoal() != null) child.setWeeklySessionGoal(request.getWeeklySessionGoal());

        if (request.getClinicianId() != null) {
            clinicianProfileRepository.findById(request.getClinicianId()).ifPresent(child::setClinician);
        }

        Child saved = childRepository.save(child);
        activityLogService.log("Child profile updated: " + saved.getName() + " by " + parent.getName());
        return ResponseEntity.ok(mapToResponse(saved));
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

        visionSessionRepository.deleteByChildId(child.getId());
        childRepository.delete(child);

        activityLogService.log("Child profile deleted: " + child.getName() + " by " + parent.getName());
        return ResponseEntity.ok().build();
    }

    // ── Clinician Mapping Endpoints ──

    @PostMapping("/{childId}/assign-clinician")
    public ResponseEntity<?> assignClinician(@PathVariable Long childId, @RequestBody Map<String, Object> request, Authentication authentication) {
        String email = authentication.getName();
        User parent = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Child child = childRepository.findById(childId)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        if (!child.getParent().getId().equals(parent.getId())) {
            return ResponseEntity.status(403).body("Unauthorized");
        }

        Long clinicianId = Long.valueOf(request.get("clinicianId").toString());
        Boolean isPrimary = request.get("isPrimary") != null ? Boolean.valueOf(request.get("isPrimary").toString()) : true;
        String notes = request.get("notes") != null ? request.get("notes").toString() : null;

        User clinicianUser = userRepository.findById(clinicianId)
                .orElseThrow(() -> new RuntimeException("Clinician user not found"));

        if (clinicianMappingRepository.existsByChildIdAndClinicianId(childId, clinicianId)) {
            return ResponseEntity.badRequest().body(Map.of("message", "Clinician already assigned to this child"));
        }

        ChildClinicianMapping mapping = ChildClinicianMapping.builder()
                .child(child)
                .clinician(clinicianUser)
                .assignedBy(parent)
                .isPrimary(isPrimary)
                .notes(notes)
                .status(MappingStatus.ACTIVE)
                .build();

        clinicianMappingRepository.save(mapping);
        activityLogService.log("Clinician " + clinicianUser.getName() + " assigned to " + child.getName() + " by " + parent.getName());

        return ResponseEntity.ok(Map.of("status", "ASSIGNED", "message", "Clinician assigned successfully"));
    }

    @GetMapping("/{childId}/clinicians")
    public ResponseEntity<List<Map<String, Object>>> getAssignedClinicians(@PathVariable Long childId) {
        List<ChildClinicianMapping> mappings = clinicianMappingRepository.findByChildId(childId);

        List<Map<String, Object>> result = mappings.stream()
                .map(m -> {
                    Map<String, Object> map = new java.util.LinkedHashMap<>();
                    map.put("mappingId", m.getId());
                    map.put("clinicianId", m.getClinician().getId());
                    map.put("clinicianName", m.getClinician().getName());
                    map.put("isPrimary", m.getIsPrimary());
                    map.put("status", m.getStatus().name());
                    map.put("assignedAt", m.getAssignedAt() != null ? m.getAssignedAt().format(DateTimeFormatter.ofPattern("MMM dd, yyyy")) : null);
                    map.put("notes", m.getNotes());
                    return map;
                })
                .collect(Collectors.toList());

        return ResponseEntity.ok(result);
    }

    @DeleteMapping("/{childId}/clinicians/{clinicianId}")
    public ResponseEntity<?> removeClinician(@PathVariable Long childId, @PathVariable Long clinicianId, Authentication authentication) {
        String email = authentication.getName();
        User parent = userRepository.findByEmail(email)
                .orElseThrow(() -> new RuntimeException("User not found"));

        Child child = childRepository.findById(childId)
                .orElseThrow(() -> new RuntimeException("Child not found"));

        if (!child.getParent().getId().equals(parent.getId())) {
            return ResponseEntity.status(403).body("Unauthorized");
        }

        ChildClinicianMapping mapping = clinicianMappingRepository.findByChildIdAndClinicianId(childId, clinicianId)
                .orElseThrow(() -> new RuntimeException("Mapping not found"));

        clinicianMappingRepository.delete(mapping);
        activityLogService.log("Clinician removed from " + child.getName() + " by " + parent.getName());

        return ResponseEntity.ok(Map.of("status", "REMOVED"));
    }

    // ── Available Clinicians (for assignment dropdown) ──

    @GetMapping("/available-clinicians")
    public ResponseEntity<List<Map<String, Object>>> getAvailableClinicians() {
        List<ClinicianProfile> profiles = clinicianProfileRepository.findByApprovalStatus("APPROVED");
        List<Map<String, Object>> result = profiles.stream()
                .filter(cp -> cp.getUser() != null)
                .map(cp -> {
                    Map<String, Object> map = new java.util.LinkedHashMap<>();
                    map.put("userId", cp.getUser().getId());
                    map.put("profileId", cp.getId());
                    map.put("name", cp.getUser().getName());
                    map.put("specialization", cp.getSpecialization());
                    map.put("organization", cp.getOrganization());
                    return map;
                })
                .collect(Collectors.toList());
        return ResponseEntity.ok(result);
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
                .diagnosis(child.getDiagnosis())
                .notes(child.getNotes())
                .avatarColor(child.getAvatarColor())
                .statusBadge(child.getStatusBadge())
                .currentFocusArea(child.getCurrentFocusArea())
                .weeklySessionGoal(child.getWeeklySessionGoal())
                .lastSessionAt(child.getLastSessionAt() != null ? child.getLastSessionAt().format(DateTimeFormatter.ofPattern("MMM dd, yyyy HH:mm")) : null)
                .build();
    }
}
