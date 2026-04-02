import React from 'react';

export default function SystemOverview({ metrics }) {
    if (!metrics) return null;

    const cards = [
        { label: 'Total Users', value: metrics.totalUsers, icon: '👥', color: '#0ea5e9' },
        { label: 'Total Children', value: metrics.totalChildren, icon: '👶', color: '#10b981' },
        { label: 'Active Sessions', value: metrics.activeSessions, icon: '⚡', color: '#f59e0b' },
    ];

    return (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 24, marginBottom: 32 }}>
            {cards.map((card, idx) => (
                <div key={idx} className="card" style={{ padding: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
                    <div style={{ background: `${card.color}15`, color: card.color, width: 48, height: 48, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 24 }}>
                        {card.icon}
                    </div>
                    <div>
                        <div style={{ color: 'var(--color-text-muted)', fontSize: 13, fontWeight: 500, marginBottom: 4 }}>{card.label}</div>
                        <div style={{ fontSize: 24, fontWeight: 700, color: 'var(--color-text-primary)' }}>{card.value}</div>
                    </div>
                </div>
            ))}
            <div className="card" style={{ padding: 24, display: 'flex', alignItems: 'center', gap: 16 }}>
                <div style={{ background: '#ecfdf5', color: '#10b981', width: 48, height: 48, borderRadius: 12, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                        <polyline points="22 4 12 14.01 9 11.01" />
                    </svg>
                </div>
                <div>
                    <div style={{ color: 'var(--color-text-muted)', fontSize: 13, fontWeight: 500, marginBottom: 4 }}>System Health</div>
                    <div style={{ fontSize: 18, fontWeight: 600, color: '#10b981' }}>{metrics.systemHealth}</div>
                </div>
            </div>
        </div>
    );
}
