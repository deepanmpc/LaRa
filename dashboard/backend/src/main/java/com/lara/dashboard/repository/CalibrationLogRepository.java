package com.lara.dashboard.repository;

import com.lara.dashboard.model.CalibrationLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface CalibrationLogRepository extends JpaRepository<CalibrationLog, Long> {
    List<CalibrationLog> findByChildIdHashedAndPredictionTypeAndTimestampAfterOrderByTimestampAsc(
            String childIdHashed, String predictionType, LocalDateTime timestamp);
}
