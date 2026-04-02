package com.lara.dashboard.entity;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Entity
@Table(name = "sessions")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Session {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String sessionId;
    private String childIdHashed;
    private Integer durationSeconds;
    private Double avgMoodConfidence;
    private Integer totalInterventions;
    private LocalDateTime startTime;
    private LocalDateTime endTime;

    // Added for Clinician Sessions
    @jakarta.persistence.Enumerated(jakarta.persistence.EnumType.STRING)
    private com.lara.dashboard.enums.SessionStatus status;

    private String interventionUsed;

    @jakarta.persistence.ManyToOne(fetch = jakarta.persistence.FetchType.LAZY)
    @jakarta.persistence.JoinColumn(name = "child_id")
    private Child child;
}
