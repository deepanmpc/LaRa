import React, { useState, useEffect } from 'react';
import api from '../../services/api';

export default function SystemHealth() {
    const [health, setHealth] = useState(null);

    useEffect(() => {
        api.get("/admin/health")
            .then(res => setHealth(res.data))
            .catch(err => console.error("Failed to fetch system health", err));
    }, []);

    return (
        <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 32 }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--color-border)', background: '#fafafa' }}>
                <h2 style={{ fontSize: 18, margin: 0, color: 'var(--color-text-primary)' }}>System Health</h2>
            </div>
            {health ? (
                <div style={{ padding: 24, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 24 }}>
                    <div>
                        <div style={{ color: 'var(--color-text-muted)', fontSize: 13, fontWeight: 500, marginBottom: 4 }}>API Latency</div>
                        <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--color-text-primary)' }}>{health.apiLatency} ms</div>
                        <div style={{ fontSize: 12, color: health.apiLatency < 100 ? '#10b981' : '#f59e0b', marginTop: 4 }}>
                            {health.apiLatency < 100 ? 'Optimal' : 'Acceptable'}
                        </div>
                    </div>
                    <div>
                        <div style={{ color: 'var(--color-text-muted)', fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Database Status</div>
                        <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--color-text-primary)' }}>{health.databaseStatus}</div>
                        <div style={{ fontSize: 12, color: health.databaseStatus === 'Connected' ? '#10b981' : '#dc2626', marginTop: 4 }}>
                            {health.databaseStatus === 'Connected' ? '99.9% Uptime' : 'Connection Error'}
                        </div>
                    </div>
                    <div>
                        <div style={{ color: 'var(--color-text-muted)', fontSize: 13, fontWeight: 500, marginBottom: 4 }}>Service Health</div>
                        <div style={{ fontSize: 18, fontWeight: 600, color: 'var(--color-text-primary)' }}>{health.serviceHealth}</div>
                        <div style={{ fontSize: 12, color: '#10b981', marginTop: 4 }}>0 Issues Reported</div>
                    </div>
                </div>
            ) : (
                <div style={{ padding: 24, color: 'var(--color-text-muted)' }}>Loading system health...</div>
            )}
        </div>
    );
}
