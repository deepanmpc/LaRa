import { useState, useEffect } from 'react';
import AdminLayout from '../../components/dashboard/AdminLayout';
import api from '../../services/api';
import { 
    BarChart, 
    Bar, 
    XAxis, 
    YAxis, 
    CartesianGrid, 
    Tooltip as RechartsTooltip, 
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    Legend
} from 'recharts';

const COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'];

export default function AdminPopulationAnalytics() {
    const [analytics, setAnalytics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const res = await api.get('/api/admin/population/analytics');
                setAnalytics(res.data);
            } catch (err) {
                console.error('Population analytics fetch failed', err);
            } finally {
                setLoading(false);
            }
        };
        fetchAnalytics();
    }, []);

    if (loading) return <AdminLayout title="Population" subtitle="Aggregating dataset..." />;

    const masteryData = Object.entries(analytics?.masteryByAgeGroup || {}).map(([age, value]) => ({
        age,
        mastery: Math.round(value)
    }));

    const engagementData = Object.entries(analytics?.engagementDistribution || {}).map(([name, value]) => ({
        name,
        value
    }));

    return (
        <AdminLayout title="Population Analytics" subtitle="Global trends and developmental benchmarks across all patients.">
            <div className="clinical-section-grid clinical-section-grid--two-column">
                <article className="clinical-panel">
                    <h3 className="clinical-panel__title">Mastery by Age Group (%)</h3>
                    <div style={{ width: '100%', height: '300px', marginTop: '24px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={masteryData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="age" axisLine={false} tickLine={false} tick={{ fontSize: 12 }} />
                                <YAxis axisLine={false} tickLine={false} tick={{ fontSize: 12 }} domain={[0, 100]} />
                                <RechartsTooltip 
                                    cursor={{ fill: '#f8fafc' }}
                                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)' }}
                                />
                                <Bar dataKey="mastery" fill="var(--color-primary)" radius={[4, 4, 0, 0]} barSize={40} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </article>

                <article className="clinical-panel">
                    <h3 className="clinical-panel__title">Engagement Distribution</h3>
                    <div style={{ width: '100%', height: '300px', marginTop: '24px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={engagementData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {engagementData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <RechartsTooltip />
                                <Legend verticalAlign="bottom" height={36}/>
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </article>
            </div>

            <article className="clinical-panel" style={{ marginTop: '32px' }}>
                <h3 className="clinical-panel__title">Intervention Success Rates</h3>
                <div style={{ marginTop: '24px' }}>
                    {Object.entries(analytics?.interventionSuccessRates || {}).map(([tool, rate]) => (
                        <div key={tool} style={{ marginBottom: '16px' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '13px', marginBottom: '6px' }}>
                                <span style={{ fontWeight: 700 }}>{tool}</span>
                                <span>{Math.round(rate * 100)}% Effectiveness</span>
                            </div>
                            <div style={{ height: '8px', background: '#f1f5f9', borderRadius: '4px', overflow: 'hidden' }}>
                                <div style={{ height: '100%', width: `${rate * 100}%`, background: rate > 0.7 ? '#10b981' : '#3b82f6', transition: 'width 1s ease' }}></div>
                            </div>
                        </div>
                    ))}
                </div>
            </article>
        </AdminLayout>
    );
}
