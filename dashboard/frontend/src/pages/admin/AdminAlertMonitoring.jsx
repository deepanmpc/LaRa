import { useState, useEffect, useCallback } from 'react';
import AdminLayout from '../../components/dashboard/AdminLayout';
import api from '../../services/api';
import { 
    AlertTriangle, 
    CheckCircle2, 
    Filter,
    Clock,
    User
} from 'lucide-react';

export default function AdminAlertMonitoring() {
    const [alerts, setAlerts] = useState([]);
    const [filter, setFilter] = useState({ severity: '', resolved: false });

    const fetchAlerts = useCallback(async () => {
        try {
            const params = new URLSearchParams();
            if (filter.severity) params.append('severity', filter.severity);
            params.append('resolved', filter.resolved);
            
            const res = await api.get(`/api/admin/alerts?${params.toString()}`);
            setAlerts(res.data);
        } catch (err) {
            console.error('Failed to fetch alerts', err);
        }
    }, [filter]);

    useEffect(() => {
        // eslint-disable-next-line
        fetchAlerts();
    }, [fetchAlerts]);

    const handleResolve = async (id) => {
        try {
            await api.post(`/api/admin/alerts/${id}/resolve`);
            fetchAlerts();
        } catch (err) {
            console.error(err);
            alert('Resolution failed'); 
        }
    };

    return (
        <AdminLayout title="Platform Alerts" subtitle="Real-time behavioral and system anomaly monitoring.">
            <div style={{ marginBottom: '24px', display: 'flex', gap: '12px' }}>
                <button 
                    className={`btn-secondary ${!filter.resolved ? 'active' : ''}`} 
                    onClick={() => setFilter({ ...filter, resolved: false })}
                    style={{ background: !filter.resolved ? 'var(--color-primary)' : '', color: !filter.resolved ? 'white' : '' }}
                >
                    Active Alerts
                </button>
                <button 
                    className={`btn-secondary ${filter.resolved ? 'active' : ''}`} 
                    onClick={() => setFilter({ ...filter, resolved: true })}
                    style={{ background: filter.resolved ? 'var(--color-primary)' : '', color: filter.resolved ? 'white' : '' }}
                >
                    Resolved
                </button>
                
                <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Filter size={16} color="var(--color-text-muted)" />
                    <select 
                        value={filter.severity} 
                        onChange={(e) => setFilter({ ...filter, severity: e.target.value })}
                        style={{ padding: '8px 12px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '13px' }}
                    >
                        <option value="">All Severities</option>
                        <option value="CRITICAL">Critical</option>
                        <option value="WARNING">Warning</option>
                        <option value="INFO">Info</option>
                    </select>
                </div>
            </div>

            <div className="alert-stack">
                {alerts.map(alert => (
                    <article key={alert.id} className="clinical-panel" style={{ marginBottom: '16px', borderLeft: `4px solid ${alert.severity === 'CRITICAL' ? '#ef4444' : alert.severity === 'WARNING' ? '#f59e0b' : '#3b82f6'}` }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                            <div style={{ display: 'flex', gap: '16px' }}>
                                <div style={{ 
                                    width: '40px', 
                                    height: '40px', 
                                    borderRadius: '10px', 
                                    background: alert.severity === 'CRITICAL' ? '#fef2f2' : alert.severity === 'WARNING' ? '#fffbeb' : '#f0f9ff',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center'
                                }}>
                                    <AlertTriangle size={20} color={alert.severity === 'CRITICAL' ? '#ef4444' : alert.severity === 'WARNING' ? '#f59e0b' : '#3b82f6'} />
                                </div>
                                <div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                        <h4 style={{ fontSize: '15px', fontWeight: 700 }}>{alert.alertType}</h4>
                                        <span style={{ fontSize: '10px', fontWeight: 800, padding: '2px 6px', borderRadius: '4px', background: '#f1f5f9' }}>{alert.severity}</span>
                                    </div>
                                    <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginTop: '4px' }}>{alert.message}</p>
                                    <div style={{ display: 'flex', gap: '16px', marginTop: '12px' }}>
                                        <span style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-muted)' }}>
                                            <User size={12} /> Child ID: {alert.childId}
                                        </span>
                                        <span style={{ fontSize: '11px', display: 'flex', alignItems: 'center', gap: '4px', color: 'var(--color-text-muted)' }}>
                                            <Clock size={12} /> {new Date(alert.createdAt).toLocaleString()}
                                        </span>
                                    </div>
                                </div>
                            </div>
                            {!alert.resolved && (
                                <button 
                                    onClick={() => handleResolve(alert.id)}
                                    style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '12px', fontWeight: 700, color: '#10b981', padding: '8px 12px', borderRadius: '8px', border: '1px solid #d1fae5' }}
                                >
                                    <CheckCircle2 size={14} /> Resolve
                                </button>
                            )}
                        </div>
                    </article>
                ))}
                {alerts.length === 0 && (
                    <div style={{ textAlign: 'center', padding: '48px', color: 'var(--color-text-muted)' }}>
                        No alerts found matching your criteria.
                    </div>
                )}
            </div>
        </AdminLayout>
    );
}
