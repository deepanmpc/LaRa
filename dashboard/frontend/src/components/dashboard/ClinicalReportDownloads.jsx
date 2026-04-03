import { Download, FileText } from 'lucide-react';
import { downloadClinicalReportPdf } from '../../utils/clinicalPdf';

export default function ClinicalReportDownloads({ reports }) {
    return (
        <div className="clinical-reports-grid">
            {reports.map((report) => (
                <article key={report.id} className="clinical-report-card">
                    <div className="clinical-report-card__header">
                        <span className="clinical-report-card__icon">
                            <FileText size={18} strokeWidth={2.2} />
                        </span>
                        <div className="clinical-report-card__header-text">
                            <h3 className="clinical-report-card__title">{report.title}</h3>
                            <div className="clinical-report-card__meta-tag">Official Record</div>
                        </div>
                        <button
                            type="button"
                            className="clinical-report-card__download-btn"
                            onClick={() => downloadClinicalReportPdf(report.title, report.lines)}
                            aria-label={`Download ${report.title}`}
                            title={`Download ${report.title}`}
                        >
                            <Download size={18} strokeWidth={2.5} />
                        </button>
                    </div>

                    <p className="clinical-report-card__summary">{report.summary}</p>

                    <div className="clinical-report-card__metrics">
                        {report.metrics.map((metric) => (
                            <span key={metric} className="clinical-report-card__metric">
                                {metric}
                            </span>
                        ))}
                    </div>
                </article>
            ))}
        </div>
    );
}
