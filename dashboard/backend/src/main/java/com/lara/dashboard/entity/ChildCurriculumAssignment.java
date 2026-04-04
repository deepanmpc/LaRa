package com.lara.dashboard.entity;

import com.lara.dashboard.enums.CurriculumAssignmentStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "child_curriculum_assignments",
       uniqueConstraints = @UniqueConstraint(columnNames = {"child_id", "topic_id"}))
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildCurriculumAssignment {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "topic_id", nullable = false)
    private CurriculumTopic topic;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assigned_by")
    private User assignedBy;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    @Column(name = "status")
    private CurriculumAssignmentStatus status = CurriculumAssignmentStatus.NOT_STARTED;

    @CreationTimestamp
    @Column(name = "assigned_at", updatable = false)
    private LocalDateTime assignedAt;

    @Column(name = "mastered_at")
    private LocalDateTime masteredAt;

    @Builder.Default
    @Column(name = "current_difficulty")
    private Integer currentDifficulty = 1;

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;
}
