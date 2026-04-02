import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';
import ClinicalReportDownloads from '../../components/dashboard/ClinicalReportDownloads';
import { clinicalStudentMock, getClinicalReports } from '../../data/clinicalStudentMock';

export default function ClinicianReports() {
    const reports = getClinicalReports(clinicalStudentMock);

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <ClinicianSidebar />

            <main className="dashboard-main clinical-student-page">
                <div className="clinical-student-page__inner">
                    <section className="clinical-section">
                        <div className="clinical-section__header">
                            <div className="clinical-section__label-row">
                                <span className="clinical-section__label">Reports</span>
                            </div>
                            <div>
                                <h1 className="clinical-section__title">Clinical Report Library</h1>
                                <p className="clinical-section__subtitle">
                                    Structured PDF summaries for cognitive, emotional, engagement, and session-level review.
                                </p>
                            </div>
                        </div>

                        <ClinicalReportDownloads reports={reports} />
                    </section>
                </div>
            </main>
        </div>
    );
}
