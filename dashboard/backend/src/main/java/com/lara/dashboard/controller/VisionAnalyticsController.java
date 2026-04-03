package com.lara.dashboard.controller;

import com.lara.dashboard.dto.VisionAnalyticsDtos;
import com.lara.dashboard.entity.EngagementTimeline;
import com.lara.dashboard.entity.VisionMetrics;
import com.lara.dashboard.entity.VisionSession;
import com.lara.dashboard.repository.EngagementTimelineRepository;
import com.lara.dashboard.repository.VisionMetricsRepository;
import com.lara.dashboard.repository.VisionSessionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/clinician")
@RequiredArgsConstructor
public class VisionAnalyticsController {

    private final VisionSessionRepository visionSessionRepository;
    private final VisionMetricsRepository visionMetricsRepository;
    private final EngagementTimelineRepository engagementTimelineRepository;

    @PostMapping("/vision/flush")
    public ResponseEntity<String> saveVisionMetrics(@RequestBody VisionAnalyticsDtos.VisionFlushRequest req) {
        VisionSession session = VisionSession.builder()
                .childId(req.getChild_id())
                .sessionUuid(req.getSession_uuid())
                .sessionType("NORMAL")
                .startedAt(LocalDateTime.now().minusSeconds(req.getDuration_seconds() != null ? req.getDuration_seconds() : 0))
                .endedAt(LocalDateTime.now())
                .durationSeconds(req.getDuration_seconds())
                .build();
        session = visionSessionRepository.save(session);

        VisionMetrics metrics = VisionMetrics.builder()
                .session(session)
                .focusedPercent(req.getFocused_percent())
                .distractedPercent(req.getDistracted_percent())
                .absentPercent(req.getAbsent_percent())
                .distractionCount(req.getDistraction_count())
                .avgEngagementScore(req.getAvg_engagement_score())
                .peakEngagementScore(req.getPeak_engagement_score())
                .gestureActivePercent(req.getGesture_active_percent())
                .presencePercent(req.getPresence_percent())
                .avgSystemConfidence(req.getAvg_system_confidence())
                .avgFps(req.getAvg_fps())
                .totalFramesProcessed(req.getTotal_frames_processed())
                .build();
        visionMetricsRepository.save(metrics);

        if (req.getEngagement_timeline() != null) {
            List<EngagementTimeline> timelines = new ArrayList<>();
            for (VisionAnalyticsDtos.TimelineBin bin : req.getEngagement_timeline()) {
                timelines.add(EngagementTimeline.builder()
                        .session(session)
                        .minuteIndex(bin.getMinute_index())
                        .avgEngagement(bin.getAvg_engagement())
                        .attentionState(bin.getAttention_state())
                        .build());
            }
            engagementTimelineRepository.saveAll(timelines);
        }

        return ResponseEntity.ok("Saved vision analytics successfully");
    }

    @GetMapping("/students/{id}/vision-metrics")
    @PreAuthorize("hasAuthority('ROLE_CLINICIAN')")
    public ResponseEntity<VisionAnalyticsDtos.VisionMetricsResponse> getStudentVisionMetrics(@PathVariable Long id) {
        Optional<VisionSession> latestSessionOpt = visionSessionRepository.findFirstByChildIdOrderByStartedAtDesc(id);

        if (latestSessionOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        VisionSession session = latestSessionOpt.get();
        Optional<VisionMetrics> metricsOpt = visionMetricsRepository.findBySessionId(session.getId());

        if (metricsOpt.isEmpty()) {
            return ResponseEntity.notFound().build();
        }

        VisionMetrics metrics = metricsOpt.get();

        // Map to Response
        VisionAnalyticsDtos.VisionMetricsResponse response = VisionAnalyticsDtos.VisionMetricsResponse.builder()
                .avg_engagement_score(metrics.getAvgEngagementScore())
                .avg_gaze_score(metrics.getFocusedPercent() != null ? metrics.getFocusedPercent() / 100.0 : 0.0) // Derived
                .system_confidence(metrics.getAvgSystemConfidence())
                .face_conf(metrics.getPresencePercent() != null ? metrics.getPresencePercent() / 100.0 : 0.85) // Mapped estimation since fine-grained not stored
                .gesture_conf(metrics.getGestureActivePercent() != null ? (metrics.getGestureActivePercent() / 100.0 > 0 ? metrics.getGestureActivePercent() / 100.0 : 0.6) : 0.6)
                .object_conf(0.85) // Stubbed object conf
                .focused_duration(session.getDurationSeconds() != null && metrics.getFocusedPercent() != null ?
                        (int)(session.getDurationSeconds() * (metrics.getFocusedPercent() / 100.0) / 60.0) : 0)
                .distraction_frames((int)(metrics.getTotalFramesProcessed() * (metrics.getDistractedPercent() / 100.0)))
                .build();

        return ResponseEntity.ok(response);
    }
}
