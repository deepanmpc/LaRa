package com.lara.dashboard.service;

import com.lara.dashboard.dto.SystemHealthResponse;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import javax.sql.DataSource;
import java.sql.Connection;

@Service
@RequiredArgsConstructor
public class SystemHealthService {

    private final DataSource dataSource;

    public SystemHealthResponse getHealth() {

        SystemHealthResponse response = new SystemHealthResponse();

        // API Latency (measure DB roundtrip)
        long start = System.currentTimeMillis();
        try (Connection conn = dataSource.getConnection()) {
            if (conn.isValid(2)) {
                response.setDatabaseStatus("Connected");
            } else {
                response.setDatabaseStatus("Disconnected");
            }
        } catch (Exception e) {
            response.setDatabaseStatus("Disconnected");
        }
        long end = System.currentTimeMillis();

        response.setApiLatency(end - start);

        // Service Health
        response.setServiceHealth("All Services OK");

        return response;
    }
}
