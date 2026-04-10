import { useState, useEffect } from 'react';
import AdminLayout from '../../components/dashboard/AdminLayout';
import api from '../../services/api';
import { 
    Activity, 
    BrainCircuit, 
    Users, 
    Database, 
    AlertCircle,
    ChevronRight
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

function StatTile({ icon, label, value, trend, tone = 'blue' }) {
    return (
        <div className={`clinical-metric-tile clinical-metric-tile--${tone}`} style={{ height: 'auto', padding: '20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <span className="clinical-metric-tile__icon" style={{ color: `var(--color-${tone})` }}>{icon}</span>
                {trend && <span style={{ fontSize: '11px', fontWeight: 700, color: trend.startsWith('+') ? '#10b981' : '#ef4444' }}>{trend}</span>}
            </div>
            <div style={{ marginTop: '12px' }}>
                <div style={{ fontSize: '24px', fontWeight: 800, color: 'var(--color-text-primary)' }}>{value}</div>
                <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)', marginTop: '4px' }}>{label}</div>
            </div>
        </div>
    );
}

export default function AdminDashboard() {
    const navigate = useNavigate();
    const [metrics, setMetrics] = useState(null);
    const [compaction, setCompaction] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [mRes, cRes] = await Promise.all([
                    api.get('/api/admin/system/metrics'),
                    api.get('/api/admin/system/compaction-status')
                ]);
                setMetrics(mRes.data);
                setCompaction(cRes.data);
            } catch (err) {
                console.error('Admin dashboard load failed', err);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    if (loading) return <AdminLayout title="Loading..." subtitle="Verifying platform integrity" />;

    return (
        <AdminLayout 
            title="Admin Command Center" 
            subtitle="Operational oversight and platform health diagnostics."
        >
            <div className="clinical-tiles-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '32px' }}>
                <StatTile 
                    icon={<Activity size={20} />} 
                    label="Runtime Latency" 
                    value={`${metrics?.runtime_latency_ms?.toFixed(0)}ms`} 
                    tone="blue"
                />
                <StatTile 
                    icon={<BrainCircuit size={20} />} 
                    label="Model Accuracy" 
                    value="88.4%" 
                    tone="green"
                />
                <StatTile 
                    icon={<Users size={20} />} 
                    label="Active Sessions" 
                    value={metrics?.active_sessions || 0} 
                    tone="blue"
                />
                <StatTile 
                    icon={<AlertCircle size={20} />} 
                    label="Alerts (24h)" 
                    value={metrics?.alerts_last_24h || 0} 
                    tone="risk"
                />
            </div>

            <div className="clinical-section-grid clinical-section-grid--two-column">
                <article className="clinical-panel">
                    <div className="clinical-panel__header" style={{ display: 'flex', justifyContent: 'space-between' }}>
                        <h3 className="clinical-panel__title">Platform Health</h3>
                        <button onClick={() => navigate('/admin/system')} style={{ color: 'var(--color-primary)', fontSize: '12px', fontWeight: 700, display: 'flex', alignItems: 'center' }}>
                            Full Report <ChevronRight size={14} />
                        </button>
                    </div>
                    <div style={{ marginTop: '16px' }}>
                        <div style={{ padding: '12px 0', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>LLM Inference</span>
                            <span style={{ fontSize: '13px', fontWeight: 700 }}>{metrics?.llm_inference_time_ms?.toFixed(0)}ms</span>
                        </div>
                        <div style={{ padding: '12px 0', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>TTS Latency</span>
                            <span style={{ fontSize: '13px', fontWeight: 700 }}>{metrics?.tts_latency_ms?.toFixed(0)}ms</span>
                        </div>
                        <div style={{ padding: '12px 0', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between' }}>
                            <span style={{ fontSize: '13px', color: 'var(--color-text-muted)' }}>DB Write Speed</span>
                            <span style={{ fontSize: '13px', fontWeight: 700 }}>{metrics?.db_write_latency_ms}ms</span>
                        </div>
                    </div>
                </article>

                <article className="clinical-panel">
                    <div className="clinical-panel__header">
                        <h3 className="clinical-panel__title">Optimization Status</h3>
                    </div>
                    <div style={{ marginTop: '16px', display: 'flex', gap: '20px' }}>
                        <div style={{ flex: 1, background: '#f8fafc', padding: '16px', borderRadius: '12px' }}>
                            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-muted)' }}>STORAGE SAVED</div>
                            <div style={{ fontSize: '20px', fontWeight: 800, marginTop: '4px' }}>{compaction?.storage_saved_mb?.toFixed(1)}MB</div>
                        </div>
                        <div style={{ flex: 1, background: '#f8fafc', padding: '16px', borderRadius: '12px' }}>
                            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--color-text-muted)' }}>RECORDS COMPACTED</div>
                            <div style={{ fontSize: '20px', fontWeight: 800, marginTop: '4px' }}>{compaction?.records_compacted}</div>
                        </div>
                    </div>
                    <div style={{ marginTop: '16px', fontSize: '12px', color: 'var(--color-text-muted)' }}>
                        Next scheduled run: <span style={{ fontWeight: 700, color: 'var(--color-text-primary)' }}>{compaction?.next_scheduled_run}</span>
                    </div>
                </article>
            </div>
        </AdminLayout>
    );
}
