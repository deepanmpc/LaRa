package com.lara.dashboard.entity;

import com.lara.dashboard.enums.DifficultyDirection;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "session_difficulty_trajectory")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SessionDifficultyTrajectory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id", nullable = false)
    private Session session;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @Column(name = "turn_number")
    private Integer turnNumber;

    @Column(name = "difficulty_before")
    private Integer difficultyBefore;

    @Column(name = "difficulty_after")
    private Integer difficultyAfter;

    @Enumerated(EnumType.STRING)
    @Column(name = "direction")
    private DifficultyDirection direction;

    @Column(name = "reason", length = 100)
    private String reason;

    @CreationTimestamp
    @Column(name = "changed_at", updatable = false)
    private LocalDateTime changedAt;
}
