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
                const dataToSet = Array.isArray(res.data) ? res.data : [];
                
                const mappedStudents = await Promise.all(dataToSet.map(async (student) => {
                    let engagementScore = null;
                    let focusedDuration = 0;
                    try {
                        const vRes = await api.get(`/clinician/students/${student.id}/vision-metrics`);
                        if (vRes.data && vRes.data.avg_engagement_score) {
                            engagementScore = Math.round(vRes.data.avg_engagement_score * 100);
                        }
                        focusedDuration = vRes.data?.focused_duration || 0;
                    } catch (e) {
                        if (e.response?.status !== 404) {
                            console.warn(`Could not fetch vision metrics for student ${student.id}`, e);
                        }
                    }

                    return {
                        ...student,
                        // Only add computed fields if the backend actually returns them
                        ...(engagementScore !== null && { engagementScore }),
                        focusedDuration
                    };
                }));
                
                setStudents(mappedStudents);
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
                                    <th style={{ padding: '16px 24px', fontWeight: 600 }}>Grade Level</th>
                                    <th style={{ padding: '16px 24px', fontWeight: 600 }}>Last Session</th>
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
                                        <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{student.gradeLevel || 'N/A'}</td>
                                        <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>{student.lastSessionDate || 'No sessions'}</td>
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
