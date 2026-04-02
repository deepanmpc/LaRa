package com.lara.dashboard.service;

import com.lara.dashboard.entity.ActivityLog;
import com.lara.dashboard.repository.ActivityLogRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class ActivityLogService {

    private final ActivityLogRepository activityLogRepository;

    public void log(String message) {
        ActivityLog log = new ActivityLog();
        log.setMessage(message);
        log.setTimestamp(LocalDateTime.now());
        activityLogRepository.save(log);
    }
}
