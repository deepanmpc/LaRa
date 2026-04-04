package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "weekly_session_summaries",
       uniqueConstraints = @UniqueConstraint(columnNames = {"child_id", "week_start_date"}))
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WeeklySessionSummary {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @Column(name = "week_start_date", nullable = false)
    private LocalDate weekStartDate;

    @Builder.Default
    @Column(name = "sessions_this_week")
    private Integer sessionsThisWeek = 0;

    @Builder.Default
    @Column(name = "total_duration_minutes")
    private Integer totalDurationMinutes = 0;

    @Column(name = "avg_mood_score")
    private Integer avgMoodScore;

    @Column(name = "avg_focus_score")
    private Integer avgFocusScore;

    @Column(name = "weekly_goal_progress")
    private Integer weeklyGoalProgress;

    @Builder.Default
    @Column(name = "activities_completed")
    private Integer activitiesCompleted = 0;

    @Column(name = "most_recent_activity")
    private String mostRecentActivity;

    @Column(name = "next_scheduled_session")
    private LocalDateTime nextScheduledSession;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;
}
