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
@Table(name = "session_analytics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionAnalytics {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @OneToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false, unique = true)
    private Session session;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    // ── Emotional Metrics ──
    @Column(name = "overall_mood_score")
    private Integer overallMoodScore;

    @Column(name = "mood_trend", length = 50)
    private String moodTrend;

    @Column(name = "primary_emotion", length = 50)
    private String primaryEmotion;

    @Column(name = "emotion_stability_score")
    private Integer emotionStabilityScore;

    @Column(name = "anxiety_level", length = 20)
    private String anxietyLevel;

    @Column(name = "self_regulation_score")
    private Integer selfRegulationScore;

    @Column(name = "positive_interactions")
    private Integer positiveInteractions;

    @Column(name = "challenging_moments")
    private Integer challengingMoments;

    // ── Emotion Breakdown Percentages ──
    @Builder.Default
    @Column(name = "pct_happy", precision = 5, scale = 2)
    private BigDecimal pctHappy = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_calm", precision = 5, scale = 2)
    private BigDecimal pctCalm = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_focused", precision = 5, scale = 2)
    private BigDecimal pctFocused = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_anxious", precision = 5, scale = 2)
    private BigDecimal pctAnxious = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_frustrated", precision = 5, scale = 2)
    private BigDecimal pctFrustrated = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_sad", precision = 5, scale = 2)
    private BigDecimal pctSad = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_neutral", precision = 5, scale = 2)
    private BigDecimal pctNeutral = BigDecimal.ZERO;

    // ── Engagement Metrics ──
    @Column(name = "focus_score")
    private Integer focusScore;

    @Column(name = "attention_span_minutes", precision = 5, scale = 2)
    private BigDecimal attentionSpanMinutes;

    @Column(name = "task_completion_rate")
    private Integer taskCompletionRate;

    @Column(name = "participation_level", length = 20)
    private String participationLevel;

    @Column(name = "distraction_frequency", length = 20)
    private String distractionFrequency;

    @Column(name = "responsiveness_score")
    private Integer responsivenessScore;

    @Column(name = "initiative_taking_score")
    private Integer initiativeTakingScore;

    @Column(name = "collaboration_score")
    private Integer collaborationScore;

    @Column(name = "weekly_goal_progress")
    private Integer weeklyGoalProgress;

    // ── Vision Analytics ──
    @Column(name = "avg_engagement_score", precision = 5, scale = 4)
    private BigDecimal avgEngagementScore;

    @Column(name = "avg_engagement_ui_score", precision = 5, scale = 4)
    private BigDecimal avgEngagementUiScore;

    @Column(name = "avg_gaze_score", precision = 5, scale = 4)
    private BigDecimal avgGazeScore;

    @Column(name = "system_confidence", precision = 5, scale = 4)
    private BigDecimal systemConfidence;

    @Builder.Default
    @Column(name = "total_distraction_frames")
    private Integer totalDistractionFrames = 0;

    @Column(name = "focused_duration_minutes", precision = 5, scale = 2)
    private BigDecimal focusedDurationMinutes;

    @Column(name = "face_confidence", precision = 5, scale = 4)
    private BigDecimal faceConfidence;

    @Column(name = "gesture_confidence", precision = 5, scale = 4)
    private BigDecimal gestureConfidence;

    @Column(name = "pose_confidence", precision = 5, scale = 4)
    private BigDecimal poseConfidence;

    @Column(name = "object_confidence", precision = 5, scale = 4)
    private BigDecimal objectConfidence;

    // ── Voice/Prosody Analytics ──
    @Column(name = "speaking_rate_wpm")
    private Integer speakingRateWpm;

    @Column(name = "vocal_volume", precision = 5, scale = 4)
    private BigDecimal vocalVolume;

    @Column(name = "speech_stability_score", precision = 5, scale = 4)
    private BigDecimal speechStabilityScore;

    @Builder.Default
    @Column(name = "pct_vocal_neutral", precision = 5, scale = 2)
    private BigDecimal pctVocalNeutral = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_vocal_arousal", precision = 5, scale = 2)
    private BigDecimal pctVocalArousal = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_vocal_withdrawal", precision = 5, scale = 2)
    private BigDecimal pctVocalWithdrawal = BigDecimal.ZERO;

    // ── Top Activities (JSON) ──
    @Column(name = "top_activities_json", columnDefinition = "TEXT")
    private String topActivitiesJson;

    // ── Session Performance ──
    @Column(name = "interaction_continuity_score", precision = 5, scale = 4)
    private BigDecimal interactionContinuityScore;

    @Column(name = "total_engagement_average", precision = 5, scale = 4)
    private BigDecimal totalEngagementAverage;

    @Builder.Default
    @Column(name = "lara_response_count")
    private Integer laraResponseCount = 0;

    @Builder.Default
    @Column(name = "child_utterance_count")
    private Integer childUtteranceCount = 0;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
