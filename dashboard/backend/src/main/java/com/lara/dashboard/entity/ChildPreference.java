package com.lara.dashboard.entity;

import com.lara.dashboard.enums.TopicSentiment;
import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.CreationTimestamp;

import java.time.LocalDateTime;

@Entity
@Table(name = "child_preferences",
       uniqueConstraints = @UniqueConstraint(columnNames = {"child_id", "topic"}))
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildPreference {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "child_id", nullable = false)
    private Child child;

    @Column(name = "topic", nullable = false)
    private String topic;

    @Enumerated(EnumType.STRING)
    @Column(name = "sentiment", nullable = false)
    private TopicSentiment sentiment;

    @CreationTimestamp
    @Column(name = "detected_at", updatable = false)
    private LocalDateTime detectedAt;
}
