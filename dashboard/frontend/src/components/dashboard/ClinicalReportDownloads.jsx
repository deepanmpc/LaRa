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
                        <div>
                            <h3 className="clinical-report-card__title">{report.title}</h3>
                            <p className="clinical-report-card__summary">{report.summary}</p>
                        </div>
                    </div>

                    <div className="clinical-report-card__metrics">
                        {report.metrics.map((metric) => (
                            <span key={metric} className="clinical-report-card__metric">
                                {metric}
                            </span>
                        ))}
                    </div>

                    <button
                        type="button"
                        className="clinical-report-card__button"
                        onClick={() => downloadClinicalReportPdf(report.title, report.lines)}
                    >
                        <Download size={16} strokeWidth={2.2} />
                        {`Download ${report.title.replace(' Report', '')}`}
                    </button>
                </article>
            ))}
        </div>
    );
}
