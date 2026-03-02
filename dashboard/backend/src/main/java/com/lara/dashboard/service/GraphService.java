package com.lara.dashboard.service;

import com.lara.dashboard.dto.KnowledgeGraphDto;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class GraphService {

    public KnowledgeGraphDto getKnowledgeGraph(String childIdHashed) {
        // Scaffolding returning the static expected DTO so the frontend can function
        return KnowledgeGraphDto.builder()
                .nodes(List.of(
                        KnowledgeGraphDto.GraphNode.builder().id("Child_" + childIdHashed).group(1).label("Child Matrix").val(50).build(),
                        KnowledgeGraphDto.GraphNode.builder().id("Concept_Math").group(2).label("Fractions ZPD").val(20).build(),
                        KnowledgeGraphDto.GraphNode.builder().id("Emotion_Frustrated").group(3).label("Frustration Peak").val(30).build(),
                        KnowledgeGraphDto.GraphNode.builder().id("Tool_Breathing").group(4).label("Deep Breathing").val(25).build()
                ))
                .links(List.of(
                        KnowledgeGraphDto.GraphLink.builder().source("Concept_Math").target("Emotion_Frustrated").strength(0.8).type("TRIGGERED_BY").color("#ef4444").build(),
                        KnowledgeGraphDto.GraphLink.builder().source("Emotion_Frustrated").target("Tool_Breathing").strength(0.9).type("MITIGATED").color("#3b82f6").build(),
                        KnowledgeGraphDto.GraphLink.builder().source("Child_" + childIdHashed).target("Concept_Math").strength(0.5).type("ENGAGED").color("#818cf8").build()
                ))
                .build();
    }
}
