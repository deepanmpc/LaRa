package com.lara.dashboard.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class StudentDto {
    private String studentIdHashed;
    private String name;
    private Integer age;
    private String preferredName;
    private LocalDateTime lastSessionDate;
}
