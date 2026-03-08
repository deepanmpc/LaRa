package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildResponse {
    private Long id;
    private String name;
    private Integer age;
    private String gradeLevel;
    private String lastSessionDate;
}
