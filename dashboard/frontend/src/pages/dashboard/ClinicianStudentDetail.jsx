import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../../services/api';
import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';
import ClinicalStudentSections from '../../components/dashboard/ClinicalStudentSections';
import { getSeededMock } from '../../data/clinicalStudentMock';

export default function ClinicianStudentDetail() {
    const navigate = useNavigate();
    const { id } = useParams();
    const [student, setStudent] = useState(null);
    const [visionData, setVisionData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);

    useEffect(() => {
        const fetchStudent = async () => {
            try {
                const response = await api.get(`/clinician/students/${id}`);
                setStudent(response.data);
                setError(false);
                
                try {
                    const visionRes = await api.get(`/clinician/students/${id}/vision-metrics`);
                    setVisionData(visionRes.data);
                } catch (vErr) {
                    console.log('No vision metrics available:', vErr);
                }
            } catch (err) {
                console.error('Failed to fetch student:', err);
                setError(true);
            } finally {
                setLoading(false);
            }
        };

        if (id) {
            fetchStudent();
        }
    }, [id]);

    if (loading) {
        return (
            <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <p>Loading...</p>
            </div>
        );
    }

    if (error || !student) {
        return (
            <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
                <p style={{ marginBottom: 16 }}>Student not found.</p>
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

    const record = getSeededMock(id, student);

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
                    </header>

                    <ClinicalStudentSections record={record} visionData={visionData} />
                </div>
            </main>
        </div>
    );
}
