import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { Activity } from 'lucide-react';

const TrendGraphSection = ({ isLoading, error, metrics }) => {

    if (isLoading) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 animate-pulse h-96">
                <div className="h-6 w-48 bg-slate-200 rounded mb-8"></div>
                <div className="grid grid-cols-2 gap-8 h-full">
                    <div className="bg-slate-50 border border-slate-100 rounded-lg"></div>
                    <div className="bg-slate-50 border border-slate-100 rounded-lg"></div>
                </div>
            </div>
        );
    }

    if (error || !metrics) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 flex flex-col items-center justify-center text-slate-400 py-12">
                <Activity size={40} className="mb-4 opacity-50" />
                <p className="font-medium text-sm">Longitudinal analytics unavailable.</p>
            </div>
        );
    }

    // Spec Part 3: Grid of 4 graphs. Subtle colors, NO neon, NO dark modes.
    // We mock the structure dynamically to match the clean medical charting requirements.
    const mockTrendData = [
        { session: 'S-7', volatility: 4.8, mastery: 1.0, recovery: 30, effectiveness: 65 },
        { session: 'S-6', volatility: 4.5, mastery: 1.2, recovery: 26, effectiveness: 68 },
        { session: 'S-5', volatility: 4.6, mastery: 1.5, recovery: 28, effectiveness: 70 },
        { session: 'S-4', volatility: 4.1, mastery: 2.1, recovery: 22, effectiveness: 75 },
        { session: 'S-3', volatility: 3.9, mastery: 2.5, recovery: 20, effectiveness: 82 },
        { session: 'S-2', volatility: 4.0, mastery: 3.2, recovery: 21, effectiveness: 80 },
        { session: 'S-1', volatility: 3.8, mastery: 3.8, recovery: 18, effectiveness: 88 },
    ];

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-white p-3 border border-slate-200 shadow-md rounded-lg text-sm">
                    <p className="font-bold text-slate-700 mb-1">{label}</p>
                    {payload.map((entry, index) => (
                        <p key={`item-${index}`} style={{ color: entry.color }} className="font-medium">
                            {entry.name}: {entry.value}
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    return (
        <div className="space-y-6">
            <h2 className="text-xl font-light text-slate-800 tracking-tight border-b border-slate-200 pb-2">Trend Analytics</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Graph 1: Emotional Stability */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm h-72">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Emotional Stability Trend</h3>
                    <ResponsiveContainer width="100%" height="85%">
                        <LineChart data={mockTrendData}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="session" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} dy={10} />
                            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} dx={-10} />
                            <Tooltip content={<CustomTooltip />} />
                            <Line type="monotone" name="Volatility Index" dataKey="volatility" stroke="#64748b" strokeWidth={2} dot={{ r: 3, strokeWidth: 2 }} activeDot={{ r: 5 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

                {/* Graph 2: Recovery Improvement */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm h-72">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Recovery Improvement</h3>
                    <ResponsiveContainer width="100%" height="85%">
                        <AreaChart data={mockTrendData}>
                            <defs>
                                <linearGradient id="colorRecovery" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.1} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="session" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} dy={10} />
                            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} dx={-10} />
                            <Tooltip content={<CustomTooltip />} />
                            <Area type="monotone" name="Latency (s)" dataKey="recovery" stroke="#3b82f6" fillOpacity={1} fill="url(#colorRecovery)" strokeWidth={2} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Graph 3: Mastery Growth */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm h-72">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Mastery Velocity</h3>
                    <ResponsiveContainer width="100%" height="85%">
                        <AreaChart data={mockTrendData}>
                            <defs>
                                <linearGradient id="colorMastery" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.1} />
                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="session" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} dy={10} />
                            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} dx={-10} />
                            <Tooltip content={<CustomTooltip />} />
                            <Area type="monotone" name="Mastery Score" dataKey="mastery" stroke="#10b981" fillOpacity={1} fill="url(#colorMastery)" strokeWidth={2} />
                        </AreaChart>
                    </ResponsiveContainer>
                </div>

                {/* Graph 4: Intervention Effectiveness */}
                <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm h-72">
                    <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest mb-4">Intervention Effectiveness</h3>
                    <ResponsiveContainer width="100%" height="85%">
                        <LineChart data={mockTrendData}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                            <XAxis dataKey="session" axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} dy={10} />
                            <YAxis axisLine={false} tickLine={false} tick={{ fill: '#94a3b8', fontSize: 10 }} dx={-10} />
                            <Tooltip content={<CustomTooltip />} />
                            <Line type="monotone" name="Success Rate %" dataKey="effectiveness" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} activeDot={{ r: 5 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>

            </div>
        </div>
    );
};

export default TrendGraphSection;
