package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "engagement_timeline")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EngagementTimeline {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "session_id")
    private VisionSession session;

    @Column(name = "minute_index")
    private Integer minuteIndex;

    @Column(name = "avg_engagement")
    private Double avgEngagement;

    @Column(name = "attention_state")
    private String attentionState;
}
