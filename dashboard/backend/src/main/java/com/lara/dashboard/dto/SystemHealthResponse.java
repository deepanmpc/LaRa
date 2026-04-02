package com.lara.dashboard.dto;

import lombok.Data;

@Data
public class SystemHealthResponse {
    private long apiLatency;
    private String databaseStatus;
    private String serviceHealth;
}
