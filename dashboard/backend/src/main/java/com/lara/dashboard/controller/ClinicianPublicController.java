package com.lara.dashboard.controller;

import com.lara.dashboard.dto.ClinicianSummaryDTO;
import com.lara.dashboard.enums.UserStatus;
import com.lara.dashboard.repository.ClinicianProfileRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.stream.Collectors;

@RestController
@RequestMapping("/api/clinicians")
@RequiredArgsConstructor
public class ClinicianPublicController {

    private final ClinicianProfileRepository clinicianProfileRepository;

    @GetMapping("/approved")
    @PreAuthorize("hasAnyAuthority('ROLE_FAMILY', 'ROLE_ADMIN')")
    public ResponseEntity<List<ClinicianSummaryDTO>> getApprovedClinicians() {
        List<ClinicianSummaryDTO> result = clinicianProfileRepository
            .findAllByUser_Status(UserStatus.APPROVED)
            .stream()
            .map(p -> ClinicianSummaryDTO.builder()
                .id(p.getId())
                .name(p.getUser() != null ? p.getUser().getName() : null)
                .organization(p.getOrganization())
                .specialization(p.getSpecialization())
                .build())
            .collect(Collectors.toList());
        return ResponseEntity.ok(result);
    }
}
