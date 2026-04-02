package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ChildRequest;
import com.lara.dashboard.dto.ChildResponse;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.repository.ChildRepository;
import com.lara.dashboard.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/children")
@RequiredArgsConstructor
public class ChildController {

    private final ChildRepository childRepository;
    private final UserRepository userRepository;
    private final com.lara.dashboard.service.ActivityLogService activityLogService;

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

        List<ChildResponse> responses = children.stream()
                .map(this::mapToResponse)
                .collect(Collectors.toList());

        return ResponseEntity.ok(responses);
    }

    private ChildResponse mapToResponse(Child child) {
        return ChildResponse.builder()
                .id(child.getId())
                .name(child.getName())
                .age(child.getAge())
                .gradeLevel(child.getGradeLevel())
                .lastSessionDate("Never") // Default mock value
                .build();
    }
}
