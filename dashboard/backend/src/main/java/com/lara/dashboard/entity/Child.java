package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import java.time.LocalDate;
import java.time.LocalDateTime;

@Entity
@Table(name = "children")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class Child {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "parent_id", nullable = false)
    private User parent;

    // Legacy FK — kept for backward compat with existing clinician assignment flow
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "clinician_id", nullable = true)
    private ClinicianProfile clinician;

    // New FK — direct user reference for assigned clinician
    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assigned_clinician_id")
    private User assignedClinician;

    @OneToMany(mappedBy = "child", cascade = CascadeType.ALL, orphanRemoval = true)
    private java.util.List<Session> sessions;

    @Column(nullable = false)
    private String name;

    @Column(nullable = false)
    private Integer age;

    @Column(name = "grade_level")
    private String gradeLevel;

    @Column(name = "date_of_birth")
    private LocalDate dateOfBirth;

    @Column(name = "diagnosis")
    private String diagnosis;

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;

    @Column(name = "avatar_color", length = 20)
    private String avatarColor;

    @Column(name = "current_focus_area")
    private String currentFocusArea;

    @Column(name = "status_badge", length = 100)
    private String statusBadge;

    @Builder.Default
    @Column(name = "weekly_session_goal")
    private Integer weeklySessionGoal = 5;

    @Column(name = "last_session_at")
    private LocalDateTime lastSessionAt;

    @CreationTimestamp
    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @UpdateTimestamp
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
