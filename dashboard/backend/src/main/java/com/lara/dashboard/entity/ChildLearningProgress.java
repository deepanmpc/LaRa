package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "child_learning_progress",
       uniqueConstraints = @UniqueConstraint(columnNames = {"child_id", "concept_name"}))
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildLearningProgress {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    private Session session;

    @Column(name = "concept_name", nullable = false)
    private String conceptName;

    @Column(name = "curriculum_area")
    private String curriculumArea;

    @Column(name = "topic_category", length = 100)
    private String topicCategory;

    // ── Mastery ──
    @Builder.Default
    @Column(name = "mastery_level")
    private Integer masteryLevel = 0;

    @Builder.Default
    @Column(name = "highest_mastery_reached")
    private Integer highestMasteryReached = 0;

    @Builder.Default
    @Column(name = "mastery_percentage", precision = 5, scale = 2)
    private BigDecimal masteryPercentage = BigDecimal.ZERO;

    @Column(name = "mastery_status", length = 50)
    private String masteryStatus;

    // ── Attempt Stats ──
    @Builder.Default
    @Column(name = "attempt_count")
    private Integer attemptCount = 0;

    @Builder.Default
    @Column(name = "success_count")
    private Integer successCount = 0;

    @Builder.Default
    @Column(name = "failure_count")
    private Integer failureCount = 0;

    @Builder.Default
    @Column(name = "success_rate", precision = 5, scale = 4)
    private BigDecimal successRate = BigDecimal.ZERO;

    // ── Time Tracking ──
    @Column(name = "first_attempted_at")
    private LocalDateTime firstAttemptedAt;

    @Column(name = "last_attempted_at")
    private LocalDateTime lastAttemptedAt;

    @Column(name = "last_success_at")
    private LocalDateTime lastSuccessAt;

    @Builder.Default
    @Column(name = "total_time_spent_seconds")
    private Integer totalTimeSpentSeconds = 0;

    // ── Difficulty ──
    @Builder.Default
    @Column(name = "current_difficulty")
    private Integer currentDifficulty = 1;

    @Builder.Default
    @Column(name = "peak_difficulty_reached")
    private Integer peakDifficultyReached = 1;
}
