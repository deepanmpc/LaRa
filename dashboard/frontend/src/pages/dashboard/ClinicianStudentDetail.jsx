import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../services/api';
import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';
import ClinicalStudentSections from '../../components/dashboard/ClinicalStudentSections';

export default function ClinicianStudentDetail() {
    const navigate = useNavigate();
    const { id } = useParams();
    const [student, setStudent] = useState(null);
    const [analytics, setAnalytics] = useState(null);
    const [riskSignals, setRiskSignals] = useState(null);
    const [knowledgeGraph, setKnowledgeGraph] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                setLoading(true);
                // Fetch basic student info
                const studentRes = await api.get(`/clinician/students/${id}`);
                setStudent(studentRes.data);

                // Fetch comprehensive analytics deep-dive
                const analyticsRes = await api.get(`/children/${id}/analytics`);
                setAnalytics(analyticsRes.data);
                
                // Fetch clinical risk signals
                try {
                    const riskRes = await api.get(`/children/${id}/risk`);
                    setRiskSignals(riskRes.data);
                } catch (error) {
                    console.log("Risk signals not available yet");
                }

                // Fetch knowledge graph
                try {
                    const graphRes = await api.get(`/children/${id}/knowledge-graph`);
                    setKnowledgeGraph(graphRes.data);
                } catch (error) {
                    console.log("Knowledge graph not available yet");
                }
                
                setError(false);
            } catch (err) {
                console.error('Failed to fetch clinician student data:', err);
                setError(true);
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchData();
        }
    }, [id]);

    if (loading) {
        return (
            <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <div className="loading-container">
                    <div className="spinner"></div>
                    <p style={{ marginTop: 16, color: 'var(--color-text-muted)' }}>Assembling Clinical Intelligence...</p>
                </div>
            </div>
        );
    }

    if (error || !student) {
        return (
            <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ marginBottom: 16 }}>Unable to load student record.</p>
                <button 
                    className="btn-primary" 
                    style={{ width: 'auto', padding: '10px 20px' }} 
                    onClick={() => navigate('/dashboard/clinical/students')}
                >
                    Back to Roster
                </button>
            </div>
        );
    }

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <ClinicianSidebar />

            <main className="dashboard-main clinical-student-page">
                <div className="clinical-student-page__inner">
                    <header className="clinical-patient-header">
                        <div className="clinical-patient-header__identity">
                            <button
                                type="button"
                                className="clinical-patient-header__back-button"
                                onClick={() => navigate('/dashboard/clinical/students')}
                                aria-label="Return to clinician roster"
                            >
                                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <line x1="19" y1="12" x2="5" y2="12" />
                                    <polyline points="12 19 5 12 12 5" />
                                </svg>
                            </button>

                            <div>
                                <h1 className="clinical-patient-header__name">{student.name}</h1>
                                <p className="clinical-patient-header__meta">
                                    {`Age ${student.age} | ID #${id} | Last Interaction: ${student.lastSessionDate || 'None'}`}
                                </p>
                            </div>
                        </div>
                        
                        {student.statusBadge && (
                            <div className={`status-badge-pill status-badge--${student.statusBadge.toLowerCase().replace(' ', '-')}`}>
                                {student.statusBadge}
                            </div>
                        )}
                    </header>

                    <ClinicalStudentSections 
                        analytics={analytics} 
                        riskSignals={riskSignals} 
                        knowledgeGraph={knowledgeGraph} 
                    />
                </div>
            </main>
        </div>
    );
}
