package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Entity
@Table(name = "child_reinforcement_metrics",
       uniqueConstraints = @UniqueConstraint(columnNames = {"child_id", "style_name"}))
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildReinforcementMetrics {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    private Session session;

    @Column(name = "style_name", nullable = false, length = 100)
    private String styleName;

    @Builder.Default
    @Column(name = "success_count")
    private Integer successCount = 0;

    @Builder.Default
    @Column(name = "total_uses")
    private Integer totalUses = 0;

    @Builder.Default
    @Column(name = "success_rate", precision = 5, scale = 4)
    private BigDecimal successRate = BigDecimal.ZERO;

    @Builder.Default
    @Column(name = "is_preferred")
    private Boolean isPreferred = false;

    @Builder.Default
    @Column(name = "total_events")
    private Integer totalEvents = 0;

    @Column(name = "last_used_at")
    private LocalDateTime lastUsedAt;
}
