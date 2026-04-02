package com.lara.dashboard.service;

import com.lara.dashboard.dto.SessionEndRequest;
import com.lara.dashboard.entity.Session;
import com.lara.dashboard.repository.SessionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class SessionService {

    private final SessionRepository sessionRepository;

    @Transactional
    public void saveSessionEnd(SessionEndRequest request) {
        Session session = sessionRepository.findBySessionId(request.getSessionUuid())
                .orElse(new Session());
        
        session.setSessionId(request.getSessionUuid());
        session.setChildIdHashed(request.getChildIdHashed());
        session.setDurationSeconds(request.getDurationSeconds());
        session.setAvgMoodConfidence(request.getAvgMoodConfidence());
        session.setTotalInterventions(request.getTotalInterventions());
        session.setEndTime(LocalDateTime.now());
        
        if (session.getStartTime() == null) {
            session.setStartTime(LocalDateTime.now().minusSeconds(request.getDurationSeconds()));
        }

        sessionRepository.save(session);
    }
}
