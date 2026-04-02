package com.lara.dashboard.repository;

import com.lara.dashboard.entity.ZpdMetric;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

@Repository
public interface ZpdMetricRepository extends JpaRepository<ZpdMetric, Long> {

    List<ZpdMetric> findByChildIdHashedAndTimestampAfterOrderByTimestampAsc(
        String childIdHashed,
        LocalDateTime timestamp
    );
}
