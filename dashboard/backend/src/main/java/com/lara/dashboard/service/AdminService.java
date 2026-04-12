package com.lara.dashboard.service;

import com.lara.dashboard.dto.ClinicianResponse;
import com.lara.dashboard.dto.ChildResponse;
import com.lara.dashboard.entity.ClinicianProfile;
import com.lara.dashboard.entity.User;
import com.lara.dashboard.entity.Child;
import com.lara.dashboard.enums.UserStatus;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import com.lara.dashboard.repository.UserRepository;
import com.lara.dashboard.repository.ChildRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Service
public class AdminService {

    private final UserRepository userRepository;
    private final ClinicianProfileRepository clinicianProfileRepository;
    private final ChildRepository childRepository;
    private final ActivityLogService activityLogService;
    private final com.lara.dashboard.repository.ActivityLogRepository activityLogRepository;
    private final com.lara.dashboard.repository.SessionRepository sessionRepository;

    public AdminService(
        UserRepository userRepository,
        ClinicianProfileRepository clinicianProfileRepository,
        ChildRepository childRepository,
        ActivityLogService activityLogService,
        com.lara.dashboard.repository.ActivityLogRepository activityLogRepository,
        com.lara.dashboard.repository.SessionRepository sessionRepository
    ) {
        this.userRepository = userRepository;
        this.clinicianProfileRepository = clinicianProfileRepository;
        this.childRepository = childRepository;
        this.activityLogService = activityLogService;
        this.activityLogRepository = activityLogRepository;
        this.sessionRepository = sessionRepository;
    }

    public List<com.lara.dashboard.entity.ActivityLog> getLogs() {
        return activityLogRepository.findTop10ByOrderByTimestampDesc();
    }

    @Transactional(readOnly = true)
    public List<User> getPendingClinicians() {
        List<User> list = userRepository.findByRoleAndStatus(com.lara.dashboard.enums.Role.ROLE_CLINICIAN, UserStatus.PENDING);
        System.out.println("Found: " + list.size());
        return list;
    }

    @Transactional(readOnly = true)
    public List<User> getAllUsers() {
        return userRepository.findAll();
    }

    @Transactional(readOnly = true)
    public List<ChildResponse> getAllChildren() {
        return childRepository.findAll().stream()
                .map(child -> ChildResponse.builder()
                        .id(child.getId())
                        .name(child.getName())
                        .age(child.getAge())
                        .gradeLevel(child.getGradeLevel())
                        .lastSessionDate(sessionRepository.findTopByChild_IdOrderByEndTimeDesc(child.getId())
                                .map(s -> s.getEndTime() != null ? s.getEndTime().format(java.time.format.DateTimeFormatter.ofPattern("MMM dd, yyyy")) : "No sessions")
                                .orElse("No sessions"))
                        .build())
                .collect(Collectors.toList());
    }

    public Map<String, Object> getSystemMetrics() {
        long totalUsers = userRepository.count();
        long totalChildren = childRepository.count();
        
        Map<String, Object> metrics = new HashMap<>();
        metrics.put("totalUsers", totalUsers);
        metrics.put("totalChildren", totalChildren);
        metrics.put("activeSessions", sessionRepository.countByStatus(com.lara.dashboard.enums.SessionStatus.IN_PROGRESS));
        metrics.put("systemHealth", "GOOD");
        return metrics;
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

        activityLogService.log("Clinician " + user.getName() + " approved");
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

        ClinicianResponse dto = new ClinicianResponse();

        dto.setId(user.getId());
        dto.setName(user.getName());
        dto.setEmail(user.getEmail());
        dto.setOrganization(profile.getOrganization());
        dto.setSpecialization(profile.getSpecialization());
        dto.setLicenseNumber(profile.getLicenseNumber());

        return dto;
    }
}
