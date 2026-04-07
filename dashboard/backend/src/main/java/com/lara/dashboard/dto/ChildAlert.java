package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.LocalDateTime;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ChildAlert {
    private Long childId;
    private String alertType;
    private String severity;
    private String message;
    private LocalDateTime timestamp;
}
