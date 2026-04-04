package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "child_vision_metrics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildVisionMetricsEntity {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private Session session;

    @Column(name = "avg_engagement_score", precision = 5, scale = 4)
    private BigDecimal avgEngagementScore;

    @Column(name = "avg_engagement_ui_score", precision = 5, scale = 4)
    private BigDecimal avgEngagementUiScore;

    @Column(name = "avg_gaze_score", precision = 5, scale = 4)
    private BigDecimal avgGazeScore;

    @Column(name = "system_confidence", precision = 5, scale = 4)
    private BigDecimal systemConfidence;

    @Column(name = "face_confidence", precision = 5, scale = 4)
    private BigDecimal faceConfidence;

    @Column(name = "gesture_confidence", precision = 5, scale = 4)
    private BigDecimal gestureConfidence;

    @Column(name = "pose_confidence", precision = 5, scale = 4)
    private BigDecimal poseConfidence;

    @Column(name = "object_confidence", precision = 5, scale = 4)
    private BigDecimal objectConfidence;

    @Builder.Default
    @Column(name = "distraction_frames")
    private Integer distractionFrames = 0;

    @Column(name = "focused_duration_minutes", precision = 5, scale = 2)
    private BigDecimal focusedDurationMinutes;

    @Builder.Default
    @Column(name = "absent_frames")
    private Integer absentFrames = 0;

    @Column(name = "dominant_gesture", length = 50)
    private String dominantGesture;

    @Column(name = "attention_state_focused_pct", precision = 5, scale = 2)
    private BigDecimal attentionStateFocusedPct;

    @Column(name = "attention_state_distracted_pct", precision = 5, scale = 2)
    private BigDecimal attentionStateDistractedPct;

    @Column(name = "attention_state_absent_pct", precision = 5, scale = 2)
    private BigDecimal attentionStateAbsentPct;

    @CreationTimestamp
    @Column(name = "recorded_at", updatable = false)
    private LocalDateTime recordedAt;
}
