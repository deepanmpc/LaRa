package com.lara.dashboard.entity;

import com.lara.dashboard.enums.MappingStatus;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "child_clinician_mapping",
       uniqueConstraints = @UniqueConstraint(columnNames = {"child_id", "clinician_id"}))
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildClinicianMapping {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "clinician_id", nullable = false)
    private User clinician;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "assigned_by", nullable = false)
    private User assignedBy;

    @CreationTimestamp
    @Column(name = "assigned_at", updatable = false)
    private LocalDateTime assignedAt;

    @Builder.Default
    @Column(name = "is_primary")
    private Boolean isPrimary = true;

    @Column(name = "notes", columnDefinition = "TEXT")
    private String notes;

    @Enumerated(EnumType.STRING)
    @Builder.Default
    @Column(name = "status")
    private MappingStatus status = MappingStatus.ACTIVE;
}
