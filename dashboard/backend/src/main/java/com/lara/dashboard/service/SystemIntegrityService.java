package com.lara.dashboard.service;

import com.lara.dashboard.dto.SystemIntegrityDto;
import com.lara.dashboard.repository.AiConfidenceLogRepository;
import com.lara.dashboard.repository.OverrideLogRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@Slf4j
@RequiredArgsConstructor
public class SystemIntegrityService {

    private final AiConfidenceLogRepository aiConfidenceLogRepository;
    private final OverrideLogRepository overrideLogRepository;

    /**
     * Evaluates the global model health across all sessions.
     * Detects degradation in AI confidence over time or sudden spikes in human overrides.
     */
    public SystemIntegrityDto evaluateSystemIntegrity() {
        LocalDateTime sevenDaysAgo = LocalDateTime.now().minusDays(7);
        LocalDateTime fourteenDaysAgo = LocalDateTime.now().minusDays(14);
        
        // Mock Implementation of Drift Mathematics
        long recentOverrides = overrideLogRepository.count(); // Placeholder for count past 7 days
        long previousOverrides = 10; // Placeholder for baseline past 14-7 days

        double overrideSpikeRatio = (previousOverrides == 0) ? 1.0 : (double) recentOverrides / previousOverrides;
        
        // Mock confidence decay: Assuming a slight loss of precision over recent unstructured inputs
        double modelDecayRate = 0.04; 
        double dataDrift = 1.12; // Kullback-Leibler (KL) divergence placeholder

        String status = "NOMINAL";
        if (modelDecayRate > 0.1 || overrideSpikeRatio > 3.0) {
            status = "CRITICAL_DECAY";
        } else if (dataDrift > 2.0 || overrideSpikeRatio > 1.5) {
            status = "WARNING_DRIFT";
        }

        return SystemIntegrityDto.builder()
                .confidenceDecayRate(modelDecayRate)
                .distributionDriftMagnitude(dataDrift)
                .recentOverridesLimitSpike((int) recentOverrides)
                .integrityStatus(status)
                .build();
    }
}
