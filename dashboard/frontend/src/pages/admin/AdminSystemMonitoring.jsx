import { useState, useEffect } from 'react';
import AdminLayout from '../../components/dashboard/AdminLayout';
import api from '../../services/api';
import { 
    LineChart, 
    Line, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip, 
    ResponsiveContainer,
    AreaChart,
    Area
} from 'recharts';
import { Clock, Cpu, Database, Zap } from 'lucide-react';

export default function AdminSystemMonitoring() {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchMetrics = async () => {
            try {
                const res = await api.get('/api/admin/system/metrics');
                setMetrics(res.data);
            } catch (err) {
                console.error('Metrics fetch failed', err);
            } finally {
                setLoading(false);
            }
        };
        fetchMetrics();
        const interval = setInterval(fetchMetrics, 5000);
        return () => clearInterval(interval);
    }, []);

    // Simulated timeline data
    const chartData = [
        { time: '10:00', latency: 450, throughput: 12 },
        { time: '10:05', latency: 480, throughput: 15 },
        { time: '10:10', latency: 420, throughput: 14 },
        { time: '10:15', latency: 510, throughput: 18 },
        { time: '10:20', latency: 490, throughput: 16 },
        { time: '10:25', latency: 460, throughput: 15 },
    ];

    if (loading) return <AdminLayout title="Monitoring" subtitle="Fetching telemetry..." />;

    return (
        <AdminLayout title="System Monitoring" subtitle="Real-time telemetry and infrastructure performance.">
            <div className="clinical-tiles-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)', marginBottom: '32px' }}>
                <div className="clinical-metric-tile clinical-metric-tile--blue">
                    <Clock size={16} color="var(--color-blue)" />
                    <div style={{ marginTop: '8px' }}>
                        <div style={{ fontSize: '20px', fontWeight: 800 }}>{metrics?.runtime_latency_ms?.toFixed(0)}ms</div>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)' }}>AVG LATENCY</div>
                    </div>
                </div>
                <div className="clinical-metric-tile clinical-metric-tile--green">
                    <Cpu size={16} color="var(--color-green)" />
                    <div style={{ marginTop: '8px' }}>
                        <div style={{ fontSize: '20px', fontWeight: 800 }}>{metrics?.llm_inference_time_ms?.toFixed(0)}ms</div>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)' }}>LLM INFERENCE</div>
                    </div>
                </div>
                <div className="clinical-metric-tile clinical-metric-tile--blue">
                    <Database size={16} color="var(--color-blue)" />
                    <div style={{ marginTop: '8px' }}>
                        <div style={{ fontSize: '20px', fontWeight: 800 }}>{metrics?.db_write_latency_ms}ms</div>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)' }}>DB WRITE</div>
                    </div>
                </div>
                <div className="clinical-metric-tile clinical-metric-tile--green">
                    <Zap size={16} color="var(--color-green)" />
                    <div style={{ marginTop: '8px' }}>
                        <div style={{ fontSize: '20px', fontWeight: 800 }}>{metrics?.event_bus_queue_size}</div>
                        <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--color-text-muted)' }}>BUS QUEUE</div>
                    </div>
                </div>
            </div>

            <div className="clinical-section-grid">
                <article className="clinical-panel clinical-panel--wide">
                    <h3 className="clinical-panel__title">Latency Timeline (ms)</h3>
                    <div style={{ width: '100%', height: '300px', marginTop: '24px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={chartData}>
                                <defs>
                                    <linearGradient id="colorLat" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1}/>
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} dy={10} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#94a3b8' }} />
                                <Tooltip 
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                                />
                                <Area type="monotone" dataKey="latency" stroke="#3b82f6" strokeWidth={3} fillOpacity={1} fill="url(#colorLat)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </article>
            </div>
        </AdminLayout>
    );
}
