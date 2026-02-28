package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SimulationRequestDto {
    private Double difficultyAdjustmentPercentage; // e.g., -10.0 for 10% decrease in task difficulty
    private Double interventionFrequencyAdjustment; // e.g., +5.0 for increasing tool deployment
    private Double reinforcementStyleAdjustment; // Scaled -1.0 to 1.0 mapping
}
