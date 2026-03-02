package com.lara.dashboard.controller;

import com.lara.dashboard.dto.clinical.ClinicalDashboardDTO;
import com.lara.dashboard.service.ClinicalDashboardService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import java.util.Optional;

import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = ClinicalDashboardController.class)
@Import(ClinicalDashboardControllerTest.SecurityTestConfig.class)
class ClinicalDashboardControllerTest {

    @org.springframework.boot.test.context.TestConfiguration
    @EnableMethodSecurity
    static class SecurityTestConfig { }

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private ClinicalDashboardService clinicalDashboardService;

    @MockBean
    private com.lara.dashboard.security.JwtUtils jwtUtils;

    @MockBean
    private com.lara.dashboard.security.UserDetailsServiceImpl userDetailsService;

    @Test
    @WithMockUser(roles = "CLINICIAN")
    void givenClinicianRole_whenGetClinicalDashboard_thenReturns200() throws Exception {
        ClinicalDashboardDTO stub = ClinicalDashboardDTO.builder().studentIdHashed("mock-student").build();
        when(clinicalDashboardService.getClinicalDashboard(anyString(), anyInt())).thenReturn(Optional.of(stub));

        mockMvc.perform(get("/api/dashboard/clinical/mock-student"))
                .andExpect(status().isOk());
    }

    @Test
    @WithMockUser(roles = "PARENT") // Equivalent to missing role
    void givenParentRole_whenGetClinicalDashboard_thenReturns403() throws Exception {
        mockMvc.perform(get("/api/dashboard/clinical/mock-student"))
                .andExpect(status().isForbidden());
    }
    
    @Test
    void givenUnauthenticated_whenGetClinicalDashboard_thenReturns401() throws Exception {
        mockMvc.perform(get("/api/dashboard/clinical/mock-student"))
                .andExpect(status().isUnauthorized());
    }
}
