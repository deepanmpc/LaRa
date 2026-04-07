import { useState } from 'react';
import AdminLayout from '../../components/dashboard/AdminLayout';
import api from '../../services/api';
import { Download, FileText, FileCode, CheckCircle } from 'lucide-react';

export default function AdminDatasetExport() {
    const [exporting, setExporting] = useState(false);
    const [lastExport, setLastExport] = useState(null);

    const handleExport = async (format) => {
        setExporting(true);
        try {
            const res = await api.get('/api/admin/export-dataset', { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([res.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', `lara_dataset_${new Date().toISOString().split('T')[0]}.${format}`);
            document.body.appendChild(link);
            link.click();
            setLastExport(new Date().toLocaleString());
        } catch (err) {
            console.error('Export failed', err);
            alert('Export failed. Check admin permissions.');
        } finally {
            setExporting(false);
        }
    };

    return (
        <AdminLayout title="Dataset Export" subtitle="Generate and download anonymized datasets for ML research and training.">
            <div className="clinical-section-grid clinical-section-grid--two-column">
                <article className="clinical-panel">
                    <h3 className="clinical-panel__title">Export Training Data</h3>
                    <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginTop: '8px' }}>
                        This will aggregate turn metrics, vision scores, and intervention outcomes into a single tabular format.
                    </p>
                    
                    <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        <button 
                            className="btn-primary" 
                            disabled={exporting}
                            onClick={() => handleExport('csv')}
                            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', height: '48px' }}
                        >
                            <FileText size={18} /> {exporting ? 'Generating...' : 'Export as CSV'}
                        </button>
                        <button 
                            className="btn-secondary" 
                            disabled={exporting}
                            onClick={() => handleExport('parquet')}
                            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', height: '48px' }}
                        >
                            <FileCode size={18} /> Export as Parquet
                        </button>
                    </div>

                    {lastExport && (
                        <div style={{ marginTop: '24px', padding: '12px', background: '#f0f9ff', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px', color: '#0369a1' }}>
                            <CheckCircle size={14} /> Last successful export: {lastExport}
                        </div>
                    )}
                </article>

                <article className="clinical-panel">
                    <h3 className="clinical-panel__title">Data Specification</h3>
                    <div style={{ marginTop: '16px' }}>
                        <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                            <div style={{ width: '4px', background: 'var(--color-primary)', borderRadius: '2px' }}></div>
                            <div>
                                <div style={{ fontSize: '13px', fontWeight: 700 }}>TURN METRICS</div>
                                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Utterance length, latency, reinforcement style</div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '12px', marginBottom: '12px' }}>
                            <div style={{ width: '4px', background: 'var(--color-green)', borderRadius: '2px' }}></div>
                            <div>
                                <div style={{ fontSize: '13px', fontWeight: 700 }}>VISION SCORES</div>
                                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Engagement, gaze, attention state</div>
                            </div>
                        </div>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <div style={{ width: '4px', background: 'var(--color-risk)', borderRadius: '2px' }}></div>
                            <div>
                                <div style={{ fontSize: '13px', fontWeight: 700 }}>OUTCOMES</div>
                                <div style={{ fontSize: '11px', color: 'var(--color-text-muted)' }}>Intervention success, mood transitions</div>
                            </div>
                        </div>
                    </div>
                </article>
            </div>
        </AdminLayout>
    );
}
