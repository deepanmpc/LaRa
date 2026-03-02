package com.lara.dashboard.service;

import com.lara.dashboard.dto.ZpdOverviewDto;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class OverviewService {

    public ZpdOverviewDto getOverviewData(String childIdHashed) {
        // Scaffolding returning the static expected DTO so the frontend can function
        return ZpdOverviewDto.builder()
                .currentAdvancementVelocity(2.4)
                .averageElasticityScore(85.2)
                .historicalTrends(List.of(
                        ZpdOverviewDto.HistoricalTrendDto.builder().timestamp("Mon").successRate(65.0).engagementFrequency(4).difficultyMA(3.0).build(),
                        ZpdOverviewDto.HistoricalTrendDto.builder().timestamp("Tue").successRate(58.0).engagementFrequency(6).difficultyMA(4.0).build(),
                        ZpdOverviewDto.HistoricalTrendDto.builder().timestamp("Wed").successRate(72.0).engagementFrequency(3).difficultyMA(3.0).build(),
                        ZpdOverviewDto.HistoricalTrendDto.builder().timestamp("Thu").successRate(81.0).engagementFrequency(8).difficultyMA(5.0).build(),
                        ZpdOverviewDto.HistoricalTrendDto.builder().timestamp("Fri").successRate(85.0).engagementFrequency(5).difficultyMA(6.0).build()
                ))
                .conceptMastery(List.of(
                        ZpdOverviewDto.ConceptMasteryDto.builder().conceptId("Phonics").masteryScore(90.0).totalAttempts(12).build(),
                        ZpdOverviewDto.ConceptMasteryDto.builder().conceptId("Math").masteryScore(65.0).totalAttempts(8).build(),
                        ZpdOverviewDto.ConceptMasteryDto.builder().conceptId("Social").masteryScore(85.0).totalAttempts(20).build(),
                        ZpdOverviewDto.ConceptMasteryDto.builder().conceptId("Logic").masteryScore(40.0).totalAttempts(5).build(),
                        ZpdOverviewDto.ConceptMasteryDto.builder().conceptId("Verbal").masteryScore(75.0).totalAttempts(15).build()
                ))
                .build();
    }
}
