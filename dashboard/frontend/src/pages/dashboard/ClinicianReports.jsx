import { useState, useEffect } from 'react';
import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';
import ClinicalReportDownloads from '../../components/dashboard/ClinicalReportDownloads';

export default function ClinicianReports() {
    const [reports, setReports] = useState([]);

    // Note: In Task 14 we integrated real session data, but a dedicated 
    // clinical reports aggregation endpoint hasn't been built yet.
    // Setting to empty array for now to fix the break.

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
