import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';

export default function ClinicianDashboard() {
    const navigate = useNavigate();
    
    const [students, setStudents] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchStudents = async () => {
            try {
                const res = await api.get('/clinician/students');
                // Ensure res.data is an array or default to empty
                const dataToSet = Array.isArray(res.data) ? res.data : [];
                setStudents(dataToSet);
            } catch (err) {
                console.error("Failed to fetch clinician students", err);
            } finally {
                setLoading(false);
            }
        };
        
        fetchStudents();
    }, []);

    // Compute metrics
    const totalStudents = students.length;
    const activeSessionsToday = 0; // Backend not returning this for clinician yet, removing mocked value
    // Assuming backend returns frustrationRisk or we keep optional mock logic if missing
    const highRiskStudents = students.filter(s => s.frustrationRisk === 'High' || s.risk === 'HIGH').length || 0;
    const avgEngagementScore = '78%'; // Allowed as mock per instruction

    const getStatusColor = (status) => {
        switch (status) {
            case 'Stable': return { bg: '#e0f2fe', text: '#0369a1' };
            case 'Improving': return { bg: '#ecfdf5', text: '#059669' };
            case 'Needs Attention': return { bg: '#fef2f2', text: '#dc2626' };
            default: return { bg: '#f1f5f9', text: '#475569' };
        }
    };

    const getRiskColor = (risk) => {
        switch (risk) {
            case 'Low': return '#059669';
            case 'Medium': return '#d97706';
            case 'High': return '#dc2626';
            default: return '#475569';
        }
    };

    if (loading) {
        return (
            <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
                <ClinicianSidebar />
                <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
                    <div style={{ color: 'var(--color-text-muted)' }}>Loading dashboard data...</div>
                </main>
            </div>
        );
    }

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <ClinicianSidebar />

            <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, overflowY: 'auto' }}>
                <div style={{ marginBottom: 32 }}>
                    <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>Clinical Overview</h1>
                    <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 16 }}>Welcome back. Here is the status of your patients.</p>
                </div>

                {/* 1. Patient Overview Panel */}
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 24, marginBottom: 32 }}>
                    <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ color: 'var(--color-text-muted)', fontSize: 14, fontWeight: 500 }}>Total Students</span>
                        <span style={{ fontSize: 32, fontWeight: 700, color: 'var(--color-text-primary)', marginTop: 8 }}>{totalStudents}</span>
                    </div>
                    <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ color: 'var(--color-text-muted)', fontSize: 14, fontWeight: 500 }}>Active Sessions Today</span>
                        <span style={{ fontSize: 32, fontWeight: 700, color: 'var(--color-text-primary)', marginTop: 8 }}>{activeSessionsToday}</span>
                    </div>
                    <div className="card" style={{ display: 'flex', flexDirection: 'column', borderLeft: '4px solid #ef4444' }}>
                        <span style={{ color: 'var(--color-text-muted)', fontSize: 14, fontWeight: 500 }}>High Risk Students</span>
                        <span style={{ fontSize: 32, fontWeight: 700, color: '#ef4444', marginTop: 8 }}>{highRiskStudents}</span>
                    </div>
                    <div className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                        <span style={{ color: 'var(--color-text-muted)', fontSize: 14, fontWeight: 500 }}>Avg Engagement Score</span>
                        <span style={{ fontSize: 32, fontWeight: 700, color: '#0ea5e9', marginTop: 8 }}>{avgEngagementScore}</span>
                    </div>
                </div>

                {/* 2. Student Monitoring Table */}
                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--color-border)', background: '#fafafa', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h2 style={{ fontSize: 18, margin: 0, color: 'var(--color-text-primary)' }}>Student Monitoring</h2>
                        <button
                            className="btn-primary"
                            style={{ padding: '8px 16px', fontSize: 14 }}
                            onClick={() => navigate('/dashboard/clinical/students')}
                        >
                            View All
                        </button>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                            <thead>
                                <tr style={{ borderBottom: '1px solid var(--color-border)', color: 'var(--color-text-muted)', fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                                    <th style={{ padding: '16px 24px', fontWeight: 600 }}>Student Name</th>
                                    <th style={{ padding: '16px 24px', fontWeight: 600 }}>Age</th>
                                    <th style={{ padding: '16px 24px', fontWeight: 600 }}>Last Session</th>
                                    <th style={{ padding: '16px 24px', fontWeight: 600 }}>Engagement</th>
                                    <th style={{ padding: '16px 24px', fontWeight: 600 }}>Frustration Risk</th>
                                    <th style={{ padding: '16px 24px', fontWeight: 600 }}>Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {students.map(student => (
                                    <tr
                                        key={student.id}
                                        style={{ borderBottom: '1px solid var(--color-border)', cursor: 'pointer', transition: 'background-color 0.2s' }}
                                        onClick={() => navigate(`/dashboard/clinical/student/${student.id}`)}
                                        onMouseOver={e => e.currentTarget.style.backgroundColor = '#f8fafc'}
                                        onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}
                                    >
                                        <td style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                                                <div style={{ width: 32, height: 32, borderRadius: 16, background: 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0369a1', fontWeight: 600, fontSize: 14 }}>
                                                    {student.name ? student.name.charAt(0) : '?'}
                                                </div>
                                                {student.name}
                                            </div>
                                        </td>
                                        <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{student.age}</td>
                                        <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{student.lastSessionDate || 'No sessions'}</td>
                                        <td style={{ padding: '16px 24px', fontSize: 14 }}>
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                                <div style={{ width: 60, height: 6, background: '#f1f5f9', borderRadius: 3, overflow: 'hidden' }}>
                                                    <div style={{ width: `${student.engagementScore || 80}%`, height: '100%', background: '#0ea5e9' }}></div>
                                                </div>
                                                <span style={{ color: 'var(--color-text-primary)' }}>{student.engagementScore || 80}%</span>
                                            </div>
                                        </td>
                                        <td style={{ padding: '16px 24px', color: getRiskColor(student.frustrationRisk || 'Low'), fontSize: 14, fontWeight: 500 }}>
                                            {student.frustrationRisk || 'Low'}
                                        </td>
                                        <td style={{ padding: '16px 24px' }}>
                                            <span style={{
                                                background: getStatusColor(student.status || 'Stable').bg,
                                                color: getStatusColor(student.status || 'Stable').text,
                                                padding: '4px 10px',
                                                borderRadius: 12,
                                                fontSize: 12,
                                                fontWeight: 600
                                            }}>
                                                {student.status || 'Stable'}
                                            </span>
                                        </td>
                                    </tr>
                                ))}
                                {students.length === 0 && (
                                    <tr>
                                        <td colSpan="6" style={{ padding: '32px 24px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                                            No students assigned yet.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    );
}
