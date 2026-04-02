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
@Table(name = "tool_interventions")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ToolIntervention {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String childIdHashed;
    private LocalDateTime timestamp;
    private String toolId;
    private String interventionType;
    private String outcome;
}
