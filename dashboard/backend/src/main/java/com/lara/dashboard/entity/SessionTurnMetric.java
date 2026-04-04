package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "session_turn_metrics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionTurnMetric {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private Session session;

    @Column(name = "turn_number", nullable = false)
    private Integer turnNumber;

    @Column(name = "timestamp", nullable = false)
    private LocalDateTime timestamp;

    @Column(name = "child_utterance", columnDefinition = "TEXT")
    private String childUtterance;

    @Column(name = "child_utterance_length")
    private Integer childUtteranceLength;

    @Column(name = "lara_response", columnDefinition = "TEXT")
    private String laraResponse;

    @Column(name = "detected_mood", length = 50)
    private String detectedMood;

    @Column(name = "mood_confidence", precision = 5, scale = 4)
    private BigDecimal moodConfidence;

    @Column(name = "regulation_state", length = 50)
    private String regulationState;

    @Column(name = "frustration_persistence", precision = 5, scale = 4)
    private BigDecimal frustrationPersistence;

    @Column(name = "stability_persistence", precision = 5, scale = 4)
    private BigDecimal stabilityPersistence;

    @Column(name = "emotional_trend_score", precision = 5, scale = 4)
    private BigDecimal emotionalTrendScore;

    @Column(name = "difficulty_level")
    private Integer difficultyLevel;

    @Column(name = "strategy_applied", length = 100)
    private String strategyApplied;

    @Column(name = "reinforcement_style", length = 100)
    private String reinforcementStyle;

    @Column(name = "tts_speed", precision = 4, scale = 2)
    private BigDecimal ttsSpeed;

    @Column(name = "prompt_build_ms")
    private Integer promptBuildMs;

    @Column(name = "inference_ms")
    private Integer inferenceMs;

    @Column(name = "tts_ms")
    private Integer ttsMs;

    @Column(name = "total_latency_ms")
    private Integer totalLatencyMs;

    @Builder.Default
    @Column(name = "vision_presence")
    private Boolean visionPresence = false;

    @Column(name = "vision_attention_state", length = 50)
    private String visionAttentionState;

    @Column(name = "vision_engagement_score", precision = 5, scale = 4)
    private BigDecimal visionEngagementScore;

    @Column(name = "vision_gesture", length = 50)
    private String visionGesture;

    @Builder.Default
    @Column(name = "vision_distraction_frames")
    private Integer visionDistractionFrames = 0;
}
