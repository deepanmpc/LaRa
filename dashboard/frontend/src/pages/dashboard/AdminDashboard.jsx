import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { logout, getStoredUser } from '../../services/authService';

export default function AdminDashboard() {
    const [pendingClinicians, setPendingClinicians] = useState([]);
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null);
    const navigate = useNavigate();
    const user = getStoredUser();

    const fetchPendingClinicians = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/clinicians/pending');
            setPendingClinicians(response.data);
        } catch (err) {
            console.error('Failed to fetch pending clinicians', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPendingClinicians();
    }, []);

    const handleApprove = async (id) => {
        try {
            setActionLoading(id);
            await api.post(`/admin/clinicians/${id}/approve`);
            await fetchPendingClinicians();
        } catch (err) {
            console.error('Failed to approve clinician', err);
        } finally {
            setActionLoading(null);
        }
    };

    const handleReject = async (id) => {
        try {
            setActionLoading(id);
            await api.post(`/admin/clinicians/${id}/reject`);
            await fetchPendingClinicians();
        } catch (err) {
            console.error('Failed to reject clinician', err);
        } finally {
            setActionLoading(null);
        }
    };

    const handleSignOut = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <aside className="sidebar">
                <div className="sidebar-logo">
                    <div className="sidebar-logo-icon">L</div>
                    <div className="sidebar-logo-text">La<span>Ra</span> Care</div>
                </div>
                <div className="sidebar-role-badge" style={{ background: '#fef08a', color: '#854d0e', marginBottom: 20 }}>Admin View</div>

                <nav className="sidebar-nav">
                    <div className="sidebar-nav-label">Management</div>
                    <button className="sidebar-nav-item active">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                            <circle cx="9" cy="7" r="4" />
                            <path d="M23 21v-2a4 4 0 00-3-3.87" />
                            <path d="M16 3.13a4 4 0 010 7.75" />
                        </svg>
                        Pending Clinicians
                    </button>
                </nav>

                <div className="sidebar-footer" style={{ marginTop: 'auto' }}>
                    <div style={{ padding: '10px 14px', marginBottom: 8 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{user?.name || 'Admin'}</div>
                        <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 2 }}>{user?.email || ''}</div>
                    </div>
                    <button className="sidebar-signout-btn" onClick={handleSignOut}>
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
                            <polyline points="16,17 21,12 16,7" />
                            <line x1="21" y1="12" x2="9" y2="12" />
                        </svg>
                        Sign Out
                    </button>
                </div>
            </aside>

            <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, overflowY: 'auto' }}>
                <div style={{ marginBottom: 32 }}>
                    <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>Admin Dashboard</h1>
                    <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 16 }}>Review and manage clinician account requests.</p>
                </div>

                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--color-border)', background: '#fafafa' }}>
                        <h2 style={{ fontSize: 18, margin: 0, color: 'var(--color-text-primary)' }}>Pending Clinicians</h2>
                    </div>

                    {loading ? (
                        <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>Loading requests...</div>
                    ) : pendingClinicians.length === 0 ? (
                        <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>
                            <svg viewBox="0 0 24 24" width="48" height="48" fill="none" stroke="#cbd5e1" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ margin: '0 auto 16px', display: 'block' }}>
                                <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
                                <polyline points="22 4 12 14.01 9 11.01" />
                            </svg>
                            No pending clinician requests at this time.
                        </div>
                    ) : (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                                <thead>
                                    <tr style={{ borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-muted)', fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                        <th style={{ padding: '16px 24px', fontWeight: 600 }}>Name</th>
                                        <th style={{ padding: '16px 24px', fontWeight: 600 }}>Email</th>
                                        <th style={{ padding: '16px 24px', fontWeight: 600 }}>Organization</th>
                                        <th style={{ padding: '16px 24px', fontWeight: 600 }}>Details</th>
                                        <th style={{ padding: '16px 24px', fontWeight: 600 }}>Signup Date</th>
                                        <th style={{ padding: '16px 24px', fontWeight: 600, textAlign: 'right' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {pendingClinicians.map(clinician => (
                                        <tr key={clinician.id} style={{ borderBottom: '1px solid var(--color-border)' }}>
                                            <td style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--color-text-primary)' }}>{clinician.name}</td>
                                            <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{clinician.email}</td>
                                            <td style={{ padding: '16px 24px', color: 'var(--color-text-primary)', fontSize: 14 }}>{clinician.organization || '-'}</td>
                                            <td style={{ padding: '16px 24px', fontSize: 14 }}>
                                                <div style={{ color: 'var(--color-text-primary)' }}>{clinician.specialization || 'General'}</div>
                                                <div style={{ color: 'var(--color-text-muted)', fontSize: 12, marginTop: 4 }}>Lic: {clinician.licenseNumber || '-'}</div>
                                            </td>
                                            <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>
                                                {new Date(clinician.createdAt).toLocaleDateString()}
                                            </td>
                                            <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                                                <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
                                                    <button
                                                        onClick={() => handleApprove(clinician.id)}
                                                        disabled={actionLoading === clinician.id}
                                                        style={{ background: '#ecfdf5', color: '#059669', border: '1px solid #a7f3d0', padding: '6px 12px', borderRadius: 6, fontWeight: 500, fontSize: 13, cursor: 'pointer' }}
                                                    >
                                                        {actionLoading === clinician.id ? '...' : 'Approve'}
                                                    </button>
                                                    <button
                                                        onClick={() => handleReject(clinician.id)}
                                                        disabled={actionLoading === clinician.id}
                                                        style={{ background: '#fef2f2', color: '#dc2626', border: '1px solid #fecaca', padding: '6px 12px', borderRadius: 6, fontWeight: 500, fontSize: 13, cursor: 'pointer' }}
                                                    >
                                                        {actionLoading === clinician.id ? '...' : 'Reject'}
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
