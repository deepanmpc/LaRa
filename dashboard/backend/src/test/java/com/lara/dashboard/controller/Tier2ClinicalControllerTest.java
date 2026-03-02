package com.lara.dashboard.controller;

import com.lara.dashboard.service.AuditLoggingService;
import com.lara.dashboard.service.Tier2ClinicalService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(controllers = Tier2ClinicalController.class)
@Import(Tier2ClinicalControllerTest.SecurityTestConfig.class)
class Tier2ClinicalControllerTest {

    @org.springframework.boot.test.context.TestConfiguration
    @EnableMethodSecurity
    static class SecurityTestConfig { }

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private Tier2ClinicalService tier2ClinicalService;

    @MockBean
    private AuditLoggingService auditLoggingService;

    @MockBean
    private com.lara.dashboard.security.JwtUtils jwtUtils;

    @MockBean
    private com.lara.dashboard.security.UserDetailsServiceImpl userDetailsService;

    @Test
    @WithMockUser(roles = "CLINICIAN", username = "dr_smith")
    void givenClinicianRole_whenGetTier2Dashboard_thenReturns200AndLogsAudit() throws Exception {
        mockMvc.perform(get("/api/tier2/clinical/student_123"))
                .andExpect(status().isOk());

        // Verify Requirement 11: Audit logging occurs
        verify(auditLoggingService).logClinicalAccess("dr_smith", "student_123", "VIEW_TIER2_DASHBOARD");
    }

    @Test
    @WithMockUser(roles = "PARENT", username = "mom_jane")
    void givenParentRole_whenGetTier2Dashboard_thenReturns403() throws Exception {
        mockMvc.perform(get("/api/tier2/clinical/student_123"))
                .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(roles = "STUDENT", username = "student_123")
    void givenStudentRole_whenGetTier2Dashboard_thenReturns403() throws Exception {
        mockMvc.perform(get("/api/tier2/clinical/student_123"))
                .andExpect(status().isForbidden());
    }
}
