package com.lara.dashboard.service;

import com.lara.dashboard.dto.SessionResponse;
import com.lara.dashboard.entity.Session;
import com.lara.dashboard.repository.SessionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
public class ClinicianService {

    private final SessionRepository sessionRepository;

    public List<SessionResponse> getAllSessions() {
        return sessionRepository.findAll()
            .stream()
            // Ensure only sessions that have an explicit child mapped from DB are correctly formatted 
            .map(this::mapToResponse)
            .toList();
    }

    private SessionResponse mapToResponse(Session session) {
        String childName = session.getChild() != null ? session.getChild().getName() : "Unknown";
        String date = session.getStartTime() != null ? session.getStartTime().format(DateTimeFormatter.ofPattern("MMM dd, yyyy")) : "Today";
        String duration = session.getDurationSeconds() != null ? (session.getDurationSeconds() / 60) + " min" : "0 min";
        
        String status = session.getStatus() != null ? 
            session.getStatus().name().substring(0, 1) + session.getStatus().name().substring(1).toLowerCase() : 
            "Completed";

        return SessionResponse.builder()
                .id(session.getId())
                .student(childName)
                .date(date)
                .duration(duration)
                .status(status)
                .intervention(session.getInterventionUsed() != null ? session.getInterventionUsed() : "None")
                .build();
    }
}
