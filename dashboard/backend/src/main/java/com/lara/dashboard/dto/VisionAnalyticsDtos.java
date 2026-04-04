package com.lara.dashboard.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

public class VisionAnalyticsDtos {

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class TimelineBin {
        private Integer minute_index;
        private Double avg_engagement;
        private String attention_state;
    }

    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class VisionFlushRequest {
        private Long child_id;
        private String session_uuid;
        private Integer duration_seconds;

        private Double focused_percent;
        private Double distracted_percent;
        private Double absent_percent;
        private Integer distraction_count;
        private Double avg_engagement_score;
        private Double peak_engagement_score;
        private Double gesture_active_percent;
        private Double presence_percent;
        private Double avg_system_confidence;
        private Double avg_fps;
        private Integer total_frames_processed;

        private List<TimelineBin> engagement_timeline;
    }
    
    @Data
    @NoArgsConstructor
    @AllArgsConstructor
    @Builder
    public static class VisionMetricsResponse {
        private Double avg_engagement_score;
        private Double avg_gaze_score; // derived from focused_percent or distraction
        private Double system_confidence;
        private Double face_conf; // simulated or mapped from system
        private Double gesture_conf; // sim/mapped
        private Double object_conf; // sim/mapped
        
        // Behavioral counts
        private Integer focused_duration; // in minutes
        private Integer distraction_frames;
    }
}
