package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "child_activity_performance",
       uniqueConstraints = @UniqueConstraint(columnNames = {"child_id", "activity_name"}))
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildActivityPerformance {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    private Session session;

    @Column(name = "activity_name", nullable = false)
    private String activityName;

    @Column(name = "curriculum_area", length = 100)
    private String curriculumArea;

    @Column(name = "score")
    private Integer score;

    @Builder.Default
    @Column(name = "completion_count")
    private Integer completionCount = 1;

    @Builder.Default
    @Column(name = "total_time_seconds")
    private Integer totalTimeSeconds = 0;

    @Column(name = "last_played_at")
    private LocalDateTime lastPlayedAt;

    @Column(name = "avg_score", precision = 5, scale = 2)
    private BigDecimal avgScore;
}
