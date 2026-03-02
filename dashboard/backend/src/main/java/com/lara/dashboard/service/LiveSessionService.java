package com.lara.dashboard.service;

import com.lara.dashboard.dto.tier2.SessionLiveMetrics;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

/**
 * Service for Part 1: LIVE SESSION ANALYTICS.
 * Keeps calculations entirely in-memory using a sliding window buffer.
 * Does NOT query databases or trigger heavy aggregations.
 */
@Service
@Slf4j
public class LiveSessionService {

    // Thread-safe in-memory cache holding the latest live metrics per session.
    // Spec requirement: "Keep all live calculations in memory"
    private final ConcurrentMap<String, SessionLiveMetrics> activeSessionsMetrics = new ConcurrentHashMap<>();

    /**
     * Retrieves the lightweight sub-100ms live metrics.
     * @param sessionId the active session ID
     * @return the current live metrics or a null/default placeholder if not active
     */
    public SessionLiveMetrics getLiveMetrics(String sessionId) {
        // Quick O(1) in-memory lookup
        return activeSessionsMetrics.getOrDefault(sessionId, buildMockLiveMetrics(sessionId));
    }

    /**
     * Accepts high-frequency (e.g. 5-10s) heartbeats from the child client
     * and updates the sliding window state.
     */
    public void updateLiveMetrics(String sessionId, SessionLiveMetrics incomingUpdate) {
        // Here we would apply short-window sliding volatility calculations on recent ticks.
        // For development/scaffolding, we immediately store the newest state.
        activeSessionsMetrics.put(sessionId, incomingUpdate);
        log.debug("Live metrics updated in-memory for session: {}", sessionId);
    }

    /**
     * Clears a session loop locally upon completion.
     */
    public void endSessionTracking(String sessionId) {
        activeSessionsMetrics.remove(sessionId);
        log.info("Cleared live memory tracking for session: {}", sessionId);
    }

    private SessionLiveMetrics buildMockLiveMetrics(String sessionId) {
        return SessionLiveMetrics.builder()
                .sessionId(sessionId)
                .emotionalState("Engaged")
                .shortWindowVolatility(0.15)
                .frustrationCount(0)
                .engagementLevel(0.85)
                .zpdPosition(4.5)
                .currentConcept("Phonics Vowels")
                .activeDifficultyLevel(3)
                .timestamp(System.currentTimeMillis())
                .build();
    }
}
