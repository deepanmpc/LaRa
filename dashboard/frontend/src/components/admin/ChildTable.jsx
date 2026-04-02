import React from 'react';

export default function ChildTable({ children, loading }) {
    if (loading) return <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>Loading children...</div>;
    
    if (!children || children.length === 0) return <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>No children found.</div>;

    return (
        <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 32 }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--color-border)', background: '#fafafa' }}>
                <h2 style={{ fontSize: 18, margin: 0, color: 'var(--color-text-primary)' }}>Manage Children</h2>
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-muted)', fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Name</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Age</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Grade Level</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Last Session</th>
                        </tr>
                    </thead>
                    <tbody>
                        {children.map(child => (
                            <tr key={child.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                                <td style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--color-text-primary)' }}>{child.name}</td>
                                <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{child.age}</td>
                                <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{child.gradeLevel || '-'}</td>
                                <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{child.lastSessionDate || '-'}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
