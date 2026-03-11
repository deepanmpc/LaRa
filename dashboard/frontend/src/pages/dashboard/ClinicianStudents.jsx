import { useNavigate } from 'react-router-dom';
import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';

const generateMockStudents = () => {
    return [
        { id: '1', name: 'Alex Johnson', age: 7, lastSession: 'Today', engagementScore: 82, riskLevel: 'Low' },
        { id: '2', name: 'Emma Smith', age: 6, lastSession: 'Yesterday', engagementScore: 65, riskLevel: 'High' },
        { id: '3', name: 'Liam Brown', age: 8, lastSession: '2 days ago', engagementScore: 91, riskLevel: 'Low' },
        { id: '4', name: 'Sophia Davis', age: 5, lastSession: 'Today', engagementScore: 74, riskLevel: 'Medium' },
        { id: '5', name: 'Noah Wilson', age: 7, lastSession: '3 days ago', engagementScore: 58, riskLevel: 'High' },
        { id: '6', name: 'Mia Martinez', age: 6, lastSession: 'Yesterday', engagementScore: 88, riskLevel: 'Low' },
        { id: '7', name: 'James Taylor', age: 9, lastSession: 'Last week', engagementScore: 61, riskLevel: 'High' },
        { id: '8', name: 'Isabella Anderson', age: 7, lastSession: 'Today', engagementScore: 79, riskLevel: 'Medium' },
    ];
};

export default function ClinicianStudents() {
    const navigate = useNavigate();
    const students = generateMockStudents();

    const getRiskBadge = (risk) => {
        switch (risk) {
            case 'Low': return { bg: '#ecfdf5', text: '#059669' };
            case 'Medium': return { bg: '#fef3c7', text: '#d97706' };
            case 'High': return { bg: '#fef2f2', text: '#dc2626' };
            default: return { bg: '#f1f5f9', text: '#475569' };
        }
    };

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <ClinicianSidebar />

            <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, overflowY: 'auto' }}>
                <div style={{ marginBottom: 32 }}>
                    <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>Patient Roster</h1>
                    <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 16 }}>Manage and monitor all your students.</p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 24 }}>
                    {students.map(student => {
                        const riskStyle = getRiskBadge(student.riskLevel);
                        return (
                            <div
                                key={student.id}
                                className="card"
                                style={{
                                    cursor: 'pointer',
                                    transition: 'transform 0.2s, box-shadow 0.2s',
                                    padding: 24,
                                    display: 'flex',
                                    flexDirection: 'column'
                                }}
                                onClick={() => navigate(`/dashboard/clinical/student/${student.id}`)}
                                onMouseOver={e => {
                                    e.currentTarget.style.transform = 'translateY(-4px)';
                                    e.currentTarget.style.boxShadow = '0 12px 24px -10px rgba(0,0,0,0.1)';
                                }}
                                onMouseOut={e => {
                                    e.currentTarget.style.transform = 'none';
                                    e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03)';
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 16 }}>
                                    <div style={{ width: 48, height: 48, borderRadius: 24, background: 'linear-gradient(135deg, #e0f2fe 0%, #7dd3fc 100%)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#0369a1', fontWeight: 600, fontSize: 18 }}>
                                        {student.name.charAt(0)}
                                    </div>
                                    <span style={{
                                        background: riskStyle.bg,
                                        color: riskStyle.text,
                                        padding: '4px 10px',
                                        borderRadius: 12,
                                        fontSize: 12,
                                        fontWeight: 600
                                    }}>
                                        {student.riskLevel} Risk
                                    </span>
                                </div>

                                <h3 style={{ fontSize: 18, margin: '0 0 4px 0', color: 'var(--color-text-primary)' }}>{student.name}</h3>
                                <p style={{ fontSize: 14, color: 'var(--color-text-muted)', margin: '0 0 16px 0' }}>Age: {student.age}</p>

                                <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 16, marginTop: 'auto' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13 }}>
                                        <span style={{ color: 'var(--color-text-muted)' }}>Engagement</span>
                                        <span style={{ fontWeight: 600, color: 'var(--color-text-primary)' }}>{student.engagementScore}%</span>
                                    </div>
                                    <div style={{ width: '100%', height: 6, background: '#f1f5f9', borderRadius: 3, overflow: 'hidden' }}>
                                        <div style={{ width: `${student.engagementScore}%`, height: '100%', background: '#0ea5e9' }}></div>
                                    </div>
                                    <div style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 12 }}>
                                        Last Session: {student.lastSession}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </main>
        </div>
    );
}
