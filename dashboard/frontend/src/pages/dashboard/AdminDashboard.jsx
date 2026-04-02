import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import { logout, getStoredUser } from '../../services/authService';

import SystemOverview from '../../components/admin/SystemOverview';
import SystemHealth from '../../components/admin/SystemHealth';
import UserTable from '../../components/admin/UserTable';
import ChildTable from '../../components/admin/ChildTable';

export default function AdminDashboard() {
    const [pendingClinicians, setPendingClinicians] = useState([]);
    const [users, setUsers] = useState([]);
    const [children, setChildren] = useState([]);
    const [systemMetrics, setSystemMetrics] = useState(null);
    const [activityLogs, setActivityLogs] = useState([]);
    
    const [loading, setLoading] = useState(true);
    const [actionLoading, setActionLoading] = useState(null);
    
    const [activeTab, setActiveTab] = useState('overview');
    
    const navigate = useNavigate();
    const user = getStoredUser();

    const fetchDashboardData = async () => {
        try {
            setLoading(true);
            const [cliniciansRes, usersRes, childrenRes, metricsRes, logsRes] = await Promise.all([
                api.get('/admin/clinicians/pending'),
                api.get('/admin/users'),
                api.get('/admin/children'),
                api.get('/admin/system'),
                api.get('/admin/logs')
            ]);
            
            setPendingClinicians(cliniciansRes.data);
            setUsers(usersRes.data);
            setChildren(childrenRes.data);
            setSystemMetrics(metricsRes.data);
            setActivityLogs(logsRes.data);
        } catch (err) {
            console.error('Failed to fetch admin data', err);
            // Fallback mock metrics if backend is not fully ready
            if (!systemMetrics) {
                setSystemMetrics({ totalUsers: 0, totalChildren: 0, activeSessions: 0, systemHealth: 'UNKNOWN' });
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const handleApprove = async (id) => {
        try {
            setActionLoading(id);
            await api.post(`/admin/clinicians/${id}/approve`);
            await fetchDashboardData();
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
            await fetchDashboardData();
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
                <div className="sidebar-role-badge" style={{ background: '#fef08a', color: '#854d0e', marginBottom: 20 }}>System Controller</div>

                <nav className="sidebar-nav">
                    <div className="sidebar-nav-label">Management</div>
                    <button 
                        className={`sidebar-nav-item ${activeTab === 'overview' ? 'active' : ''}`}
                        onClick={() => setActiveTab('overview')}
                    >
                        Dashboard
                    </button>
                    <button 
                        className={`sidebar-nav-item ${activeTab === 'approvals' ? 'active' : ''}`}
                        onClick={() => setActiveTab('approvals')}
                    >
                        Clinician Approvals
                        {pendingClinicians.length > 0 && (
                            <span style={{ marginLeft: 'auto', background: '#dc2626', color: 'white', borderRadius: 10, padding: '2px 6px', fontSize: 10 }}>
                                {pendingClinicians.length}
                            </span>
                        )}
                    </button>
                    <button 
                        className={`sidebar-nav-item ${activeTab === 'users' ? 'active' : ''}`}
                        onClick={() => setActiveTab('users')}
                    >
                        Users & Roles
                    </button>
                    <button 
                        className={`sidebar-nav-item ${activeTab === 'children' ? 'active' : ''}`}
                        onClick={() => setActiveTab('children')}
                    >
                        Children Database
                    </button>
                </nav>

                <div className="sidebar-footer" style={{ marginTop: 'auto' }}>
                    <div style={{ padding: '10px 14px', marginBottom: 8 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{user?.name || 'Admin'}</div>
                        <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 2 }}>{user?.email || ''}</div>
                    </div>
                    <button className="sidebar-signout-btn" onClick={handleSignOut}>
                        Sign Out
                    </button>
                </div>
            </aside>

            <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, overflowY: 'auto' }}>
                <div style={{ marginBottom: 32 }}>
                    <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>Admin Control Center</h1>
                    <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 16 }}>Manage platform data, users, and oversee system health.</p>
                </div>

                {activeTab === 'overview' && (
                    <>
                        <SystemOverview metrics={systemMetrics} />
                        <SystemHealth />
                        
                        <div className="card" style={{ padding: 24, marginBottom: 32 }}>
                            <h2 style={{ fontSize: 18, margin: '0 0 16px 0', color: 'var(--color-text-primary)' }}>Activity Logs</h2>
                            <div style={{ color: 'var(--color-text-muted)', fontSize: 14 }}>
                                {activityLogs.length === 0 ? (
                                    <div style={{ padding: '12px 0' }}>No recent activity.</div>
                                ) : (
                                    activityLogs.map((log) => (
                                        <div key={log.id} style={{ padding: '12px 0', borderBottom: '1px solid var(--color-border)' }}>
                                            • {log.message} <span style={{fontSize: 12, color: '#94a3b8', marginLeft: 8}}>{new Date(log.timestamp).toLocaleString()}</span>
                                        </div>
                                    ))
                                )}
                            </div>
                        </div>
                    </>
                )}

                {activeTab === 'users' && <UserTable users={users} loading={loading} />}
                
                {activeTab === 'children' && <ChildTable children={children} loading={loading} />}

                {activeTab === 'approvals' && (
                    <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--color-border)', background: '#fafafa' }}>
                            <h2 style={{ fontSize: 18, margin: 0, color: 'var(--color-text-primary)' }}>Pending Clinicians</h2>
                        </div>

                        {loading ? (
                            <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>Loading requests...</div>
                        ) : pendingClinicians.length === 0 ? (
                            <div style={{ padding: 40, textAlign: 'center', color: 'var(--color-text-muted)' }}>
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
                                            <th style={{ padding: '16px 24px', fontWeight: 600 }}>Signup</th>
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
                )}
            </main>
        </div>
    );
}
