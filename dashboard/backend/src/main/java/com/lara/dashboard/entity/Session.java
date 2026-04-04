package com.lara.dashboard.entity;

import com.lara.dashboard.enums.SessionStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "sessions")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Session {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "session_uuid", unique = true, length = 36)
    private String sessionUuid;

    // Legacy field — kept for backward compat
    @Column(name = "session_id")
    private String sessionId;

    // Legacy field — kept for backward compat
    @Column(name = "child_id_hashed")
    private String childIdHashed;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id")
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "clinician_id")
    private User clinicianUser;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id")
    private User parentUser;

    @Column(name = "start_time")
    private LocalDateTime startTime;

    @Column(name = "end_time")
    private LocalDateTime endTime;

    @Column(name = "duration_seconds")
    private Integer durationSeconds;

    @Builder.Default
    @Column(name = "total_turns")
    private Integer totalTurns = 0;

    @Builder.Default
    @Column(name = "peak_difficulty")
    private Integer peakDifficulty = 1;

    @Builder.Default
    @Column(name = "avg_engagement_score", precision = 5, scale = 4)
    private BigDecimal avgEngagementScore = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "avg_mood_confidence", precision = 5, scale = 4)
    private BigDecimal avgMoodConfidenceNew = BigDecimal.ZERO;

    // Legacy field — kept for backward compat
    @Column(name = "avg_mood_conf_legacy")
    private Double avgMoodConfidence;

    @Builder.Default
    @Column(name = "dominant_mood", length = 50)
    private String dominantMood = "neutral";

    @Builder.Default
    @Column(name = "total_interventions")
    private Integer totalInterventions = 0;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    @Column(name = "completion_status")
    private SessionStatus completionStatus = SessionStatus.IN_PROGRESS;

    // Legacy field — kept for backward compat
    @Enumerated(EnumType.STRING)
    @Column(name = "status")
    private SessionStatus status;

    @Column(name = "session_notes", columnDefinition = "TEXT")
    private String sessionNotes;

    // Legacy field
    @Column(name = "intervention_used")
    private String interventionUsed;

    @Builder.Default
    @Column(name = "wake_word_triggers")
    private Integer wakeWordTriggers = 0;

    @Builder.Default
    @Column(name = "barge_in_count")
    private Integer bargeInCount = 0;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
