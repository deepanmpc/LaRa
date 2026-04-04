package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "child_engagement_history")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildEngagementHistory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    private Session session;

    @Column(name = "recorded_date", nullable = false)
    private LocalDate recordedDate;

    @Column(name = "focus_score")
    private Integer focusScore;

    @Column(name = "attention_span_minutes", precision = 5, scale = 2)
    private BigDecimal attentionSpanMinutes;

    @Column(name = "engagement_score", precision = 5, scale = 4)
    private BigDecimal engagementScore;

    @Column(name = "gaze_score", precision = 5, scale = 4)
    private BigDecimal gazeScore;

    @Column(name = "task_completion_rate")
    private Integer taskCompletionRate;

    @Builder.Default
    @Column(name = "distraction_frames")
    private Integer distractionFrames = 0;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
