package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "vision_metrics")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class VisionMetrics {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    private VisionSession session;

    @Column(name = "focused_percent")
    private Double focusedPercent;

    @Column(name = "distracted_percent")
    private Double distractedPercent;

    @Column(name = "absent_percent")
    private Double absentPercent;

    @Column(name = "distraction_count")
    private Integer distractionCount;

    @Column(name = "avg_engagement_score")
    private Double avgEngagementScore;

    @Column(name = "peak_engagement_score")
    private Double peakEngagementScore;

    @Column(name = "gesture_active_percent")
    private Double gestureActivePercent;

    @Column(name = "presence_percent")
    private Double presencePercent;

    @Column(name = "avg_system_confidence")
    private Double avgSystemConfidence;

    @Column(name = "avg_fps")
    private Double avgFps;

    @Column(name = "total_frames_processed")
    private Integer totalFramesProcessed;
}
