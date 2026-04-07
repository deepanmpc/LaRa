package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "student_longitudinal_metrics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class StudentLongitudinalMetrics {

    @Id
    @Column(name = "student_id", nullable = false)
    private String studentId;

    @Column(name = "rolling_volatility7")
    private Double rollingVolatility7;

    @Column(name = "rolling_volatility14")
    private Double rollingVolatility14;

    @Column(name = "recovery_trend")
    private Double recoveryTrend;

    @Column(name = "mastery_velocity")
    private Double masteryVelocity;

    @Column(name = "intervention_decay_index")
    private Double interventionDecayIndex;

    @Column(name = "frustration_risk_score")
    private Double frustrationRiskScore;

    @Column(name = "independence_score")
    private Double independenceScore;

    @Column(name = "confidence_band_high")
    private Double confidenceBandHigh;

    @Column(name = "confidence_band_low")
    private Double confidenceBandLow;

    @UpdateTimestamp
    @Column(name = "last_updated")
    private LocalDateTime lastUpdated;
}
