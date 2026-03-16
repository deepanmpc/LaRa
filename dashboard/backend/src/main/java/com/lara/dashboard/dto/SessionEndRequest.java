package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SessionEndRequest {
    private String sessionUuid;
    private String childIdHashed;
    private Integer durationSeconds;
    private Double avgMoodConfidence;
    private Integer totalInterventions;
}
