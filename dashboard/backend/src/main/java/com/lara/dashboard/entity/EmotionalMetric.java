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
@Table(name = "emotional_metrics")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class EmotionalMetric {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String childIdHashed;
    private LocalDateTime timestamp;
    private Integer moodScore;
    private String primaryEmotion;
}
