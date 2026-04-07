package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDate;

@Entity
@Table(name = "session_summary_metrics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionSummaryMetric {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "child_id_hashed", nullable = false, length = 64)
    private String childIdHashed;

    @Column(name = "summary_date", nullable = false)
    private LocalDate summaryDate;

    @Column(name = "average_volatility_that_day")
    private Double averageVolatilityThatDay;

    @Column(name = "cumulative_time_in_zpd_percentage")
    private Double cumulativeTimeInZpdPercentage;

    @Column(name = "highest_difficulty_reached")
    private Integer highestDifficultyReached;

    @Column(name = "intervention_success_rate")
    private Double interventionSuccessRate;

    @Column(name = "rolling_avg_recovery_seconds")
    private Double rollingAvgRecoverySeconds;

    @Column(name = "rolling_frustration_spikes")
    private Integer rollingFrustrationSpikes;

    @Column(name = "total_sessions_that_day")
    private Integer totalSessionsThatDay;
}
