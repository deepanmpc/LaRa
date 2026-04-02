import React from 'react';

export default function UserTable({ users, loading }) {
    if (loading) return <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>Loading users...</div>;
    
    if (!users || users.length === 0) return <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>No users found.</div>;

    return (
        <div className="card" style={{ padding: 0, overflow: 'hidden', marginBottom: 32 }}>
            <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--color-border)', background: '#fafafa' }}>
                <h2 style={{ fontSize: 18, margin: 0, color: 'var(--color-text-primary)' }}>Mange Users</h2>
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                    <thead>
                        <tr style={{ borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-muted)', fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Name</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Email</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Role</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Status</th>
                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Joined</th>
                        </tr>
                    </thead>
                    <tbody>
                        {users.map(u => (
                            <tr key={u.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                                <td style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--color-text-primary)' }}>{u.name}</td>
                                <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{u.email}</td>
                                <td style={{ padding: '16px 24px', color: 'var(--color-text-primary)', fontSize: 14 }}>
                                    <span style={{
                                        background: u.role === 'ROLE_ADMIN' ? '#fef08a' : (u.role === 'ROLE_CLINICIAN' ? '#e0e7ff' : '#f1f5f9'),
                                        color: u.role === 'ROLE_ADMIN' ? '#854d0e' : (u.role === 'ROLE_CLINICIAN' ? '#3730a3' : '#475569'),
                                        padding: '4px 10px', borderRadius: 12, fontSize: 11, fontWeight: 600
                                    }}>
                                        {u.role.replace('ROLE_', '')}
                                    </span>
                                </td>
                                <td style={{ padding: '16px 24px', fontSize: 14 }}>
                                    <span style={{
                                        color: u.status === 'APPROVED' ? '#059669' : (u.status === 'PENDING' ? '#d97706' : '#dc2626'),
                                        fontWeight: 500
                                    }}>{u.status}</span>
                                </td>
                                <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>
                                    {new Date(u.createdAt).toLocaleDateString()}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
