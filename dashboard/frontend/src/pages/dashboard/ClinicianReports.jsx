import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';

export default function ClinicianReports() {

    const mockReports = [
        { id: 1, title: 'Weekly Progress Report - All Patients', date: 'Oct 24, 2023', type: 'PDF', size: '2.4 MB' },
        { id: 2, title: 'Engagement Trends Q3', date: 'Oct 15, 2023', type: 'CSV', size: '156 KB' },
        { id: 3, title: 'Risk Forecast Assessment', date: 'Oct 08, 2023', type: 'PDF', size: '1.8 MB' },
        { id: 4, title: 'Monthly Patient Summary September', date: 'Oct 01, 2023', type: 'PDF', size: '3.1 MB' },
    ];

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <ClinicianSidebar />

            <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, overflowY: 'auto' }}>
                <div style={{ marginBottom: 32 }}>
                    <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>Reports & Exports</h1>
                    <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 16 }}>Download mock analytics and progress reports.</p>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 16 }}>
                    {mockReports.map(report => (
                        <div key={report.id} className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '20px 24px' }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
                                <div style={{ width: 44, height: 44, borderRadius: 8, background: report.type === 'PDF' ? '#fee2e2' : '#dcfce3', display: 'flex', alignItems: 'center', justifyContent: 'center', color: report.type === 'PDF' ? '#ef4444' : '#22c55e' }}>
                                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                        <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                                        <polyline points="14 2 14 8 20 8" />
                                        <line x1="16" y1="13" x2="8" y2="13" />
                                        <line x1="16" y1="17" x2="8" y2="17" />
                                        <polyline points="10 9 9 9 8 9" />
                                    </svg>
                                </div>
                                <div>
                                    <h3 style={{ fontSize: 16, margin: '0 0 4px 0', color: 'var(--color-text-primary)' }}>{report.title}</h3>
                                    <p style={{ fontSize: 13, color: 'var(--color-text-muted)', margin: 0 }}>
                                        {report.date} &bull; {report.type} &bull; {report.size}
                                    </p>
                                </div>
                            </div>
                            <button className="btn-primary" style={{ padding: '8px 16px', background: 'transparent', color: '#0ea5e9', border: '1px solid #bae6fd' }} onClick={() => alert('Mock download initiated.')}>
                                Download
                            </button>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
