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
@Table(name = "child_voice_metrics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildVoiceMetrics {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private Session session;

    @Column(name = "avg_speaking_rate_wpm")
    private Integer avgSpeakingRateWpm;

    @Column(name = "avg_volume", precision = 5, scale = 4)
    private BigDecimal avgVolume;

    @Column(name = "speech_stability_score", precision = 5, scale = 4)
    private BigDecimal speechStabilityScore;

    @Builder.Default
    @Column(name = "utterance_count")
    private Integer utteranceCount = 0;

    @Column(name = "avg_utterance_length_words", precision = 5, scale = 2)
    private BigDecimal avgUtteranceLengthWords;

    @Builder.Default
    @Column(name = "pct_vocal_neutral", precision = 5, scale = 2)
    private BigDecimal pctVocalNeutral = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_vocal_arousal", precision = 5, scale = 2)
    private BigDecimal pctVocalArousal = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "pct_vocal_withdrawal", precision = 5, scale = 2)
    private BigDecimal pctVocalWithdrawal = BigDecimal.ZERO;

    @CreationTimestamp
    @Column(name = "recorded_at", updatable = false)
    private LocalDateTime recordedAt;
}
