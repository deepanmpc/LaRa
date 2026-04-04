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
@Table(name = "child_emotional_history")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildEmotionalHistory {

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

    @Column(name = "mood_score")
    private Integer moodScore;

    @Column(name = "primary_emotion", length = 50)
    private String primaryEmotion;

    @Builder.Default
    @Column(name = "frustration_count")
    private Integer frustrationCount = 0;

    @Builder.Default
    @Column(name = "recovery_count")
    private Integer recoveryCount = 0;

    @Builder.Default
    @Column(name = "stability_count")
    private Integer stabilityCount = 0;

    @Builder.Default
    @Column(name = "anxiety_count")
    private Integer anxietyCount = 0;

    @Builder.Default
    @Column(name = "happy_count")
    private Integer happyCount = 0;

    @Builder.Default
    @Column(name = "calm_count")
    private Integer calmCount = 0;

    @Builder.Default
    @Column(name = "focused_count")
    private Integer focusedCount = 0;

    @Column(name = "pct_positive", precision = 5, scale = 2)
    private BigDecimal pctPositive;

    @Column(name = "pct_negative", precision = 5, scale = 2)
    private BigDecimal pctNegative;

    @Column(name = "regulation_index", precision = 5, scale = 2)
    private BigDecimal regulationIndex;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
