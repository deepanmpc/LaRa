package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;
import java.math.BigDecimal;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TurnMetricDTO {
    private Integer turnNumber;
    private String childUtterance;
    private String laraResponse;
    private String mood;
    private BigDecimal engagement;
    private String strategy;
}