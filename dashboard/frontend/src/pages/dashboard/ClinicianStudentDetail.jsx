import { useParams, useNavigate } from 'react-router-dom';
import { useMemo } from 'react';
import {
    LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer
} from 'recharts';
import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';

// Simple deterministic random generator based on a string seed
function seededRandom(seedStr) {
    let hash = 0;
    for (let i = 0; i < seedStr.length; i++) {
        hash = ((hash << 5) - hash) + seedStr.charCodeAt(i);
        hash |= 0;
    }
    return () => {
        hash = Math.sin(hash) * 10000;
        return hash - Math.floor(hash);
    };
}

export default function ClinicianStudentDetail() {
    const { id } = useParams();
    const navigate = useNavigate();

    // Generate deterministic mock data for charts based on student ID
    const { emotionalTrend, engagementTrend, frustrationEvents, masteryVelocity, studentInfo } = useMemo(() => {
        const rng = seededRandom(id || 'default');

        // Student Info
        const info = {
            name: `Student ${id.substring(0, 4)}`,
            age: Math.floor(rng() * 5) + 5, // 5 to 9
            diagnosed: 'ASD Level 1',
            startDate: 'Sept 2023'
        };

        const sessions = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7'];

        const emTrend = sessions.map(s => ({
            name: s,
            score: Math.floor(rng() * 40) + 60 // 60 to 100
        }));

        const engTrend = sessions.map(s => ({
            name: s,
            score: Math.floor(rng() * 50) + 50 // 50 to 100
        }));

        const frEvents = sessions.map(s => ({
            name: s,
            count: Math.floor(rng() * 5) // 0 to 4
        }));

        const mastVel = sessions.map(s => ({
            name: s,
            score: Math.floor(rng() * 30) + (sessions.indexOf(s) * 10) // progressive
        }));

        return {
            studentInfo: info,
            emotionalTrend: emTrend,
            engagementTrend: engTrend,
            frustrationEvents: frEvents,
            masteryVelocity: mastVel
        };
    }, [id]);

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <ClinicianSidebar />

            <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, overflowY: 'auto' }}>
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: 32 }}>
                    <button
                        onClick={() => navigate('/dashboard/clinical/students')}
                        style={{ marginRight: 16, background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', color: 'var(--color-text-muted)', padding: 8, borderRadius: 8 }}
                        onMouseOver={e => e.currentTarget.style.background = '#f1f5f9'}
                        onMouseOut={e => e.currentTarget.style.background = 'none'}
                    >
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <line x1="19" y1="12" x2="5" y2="12" />
                            <polyline points="12 19 5 12 12 5" />
                        </svg>
                    </button>
                    <div>
                        <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 4px 0' }}>{studentInfo.name}</h1>
                        <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 14 }}>
                            Age: {studentInfo.age} &bull; {studentInfo.diagnosed} &bull; Started {studentInfo.startDate}
                        </p>
                    </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(1, 1fr)', gap: 24, '@media (min-width: 1024px)': { gridTemplateColumns: 'repeat(2, 1fr)' } }}>

                    {/* Emotional Trend */}
                    <div className="card">
                        <h3 style={{ fontSize: 16, color: 'var(--color-text-primary)', margin: '0 0 20px 0' }}>Emotional Trend</h3>
                        <div style={{ height: 300, width: '100%' }}>
                            <ResponsiveContainer>
                                <LineChart data={emotionalTrend} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dx={-10} />
                                    <Tooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
                                    <Line type="monotone" dataKey="score" stroke="#10b981" strokeWidth={3} dot={{ r: 4, fill: '#10b981', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Engagement Trend */}
                    <div className="card">
                        <h3 style={{ fontSize: 16, color: 'var(--color-text-primary)', margin: '0 0 20px 0' }}>Engagement Trend</h3>
                        <div style={{ height: 300, width: '100%' }}>
                            <ResponsiveContainer>
                                <LineChart data={engagementTrend} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dx={-10} />
                                    <Tooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
                                    <Line type="monotone" dataKey="score" stroke="#0ea5e9" strokeWidth={3} dot={{ r: 4, fill: '#0ea5e9', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Frustration Events */}
                    <div className="card">
                        <h3 style={{ fontSize: 16, color: 'var(--color-text-primary)', margin: '0 0 20px 0' }}>Frustration Events</h3>
                        <div style={{ height: 300, width: '100%' }}>
                            <ResponsiveContainer>
                                <BarChart data={frustrationEvents} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dx={-10} allowDecimals={false} />
                                    <Tooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} cursor={{ fill: '#f1f5f9' }} />
                                    <Bar dataKey="count" fill="#ef4444" radius={[4, 4, 0, 0]} barSize={32} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                    {/* Mastery Velocity */}
                    <div className="card">
                        <h3 style={{ fontSize: 16, color: 'var(--color-text-primary)', margin: '0 0 20px 0' }}>Mastery Velocity</h3>
                        <div style={{ height: 300, width: '100%' }}>
                            <ResponsiveContainer>
                                <LineChart data={masteryVelocity} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                                    <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dy={10} />
                                    <YAxis axisLine={false} tickLine={false} tick={{ fill: '#64748b', fontSize: 12 }} dx={-10} />
                                    <Tooltip contentStyle={{ borderRadius: 8, border: 'none', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)' }} />
                                    <Line type="monotone" dataKey="score" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4, fill: '#8b5cf6', strokeWidth: 2, stroke: '#fff' }} activeDot={{ r: 6 }} />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>

                </div>
            </main>
        </div>
    );
}
