package com.lara.dashboard.entity;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Entity
@Table(name = "curriculum_topics")
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CurriculumTopic {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "name", unique = true, nullable = false)
    private String name;

    @Column(name = "area", nullable = false, length = 100)
    private String area;

    @Column(name = "description", columnDefinition = "TEXT")
    private String description;

    @Builder.Default
    @Column(name = "difficulty_min")
    private Integer difficultyMin = 1;

    @Builder.Default
    @Column(name = "difficulty_max")
    private Integer difficultyMax = 5;

    @Builder.Default
    @Column(name = "age_range_min")
    private Integer ageRangeMin = 2;

    @Builder.Default
    @Column(name = "age_range_max")
    private Integer ageRangeMax = 18;

    @Builder.Default
    @Column(name = "is_active")
    private Boolean isActive = true;
}
