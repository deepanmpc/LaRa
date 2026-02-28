import React, { useState } from 'react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar, Cell
} from 'recharts';
import { AlertTriangle, Clock, Activity, ShieldAlert } from 'lucide-react';

const Emotions = () => {
    // Mocking the EmotionalOverviewDto from Spring Boot
    const [data] = useState({
        emotionalVolatilityIndex: 4.8,
        avgRecoveryLatencyMinutes: 2.5,
        resilienceGrowthIndex: 1.15,
        heatmapCalendar: [
            { date: "02-14", dominantMood: "neutral", spikeCount: 0, stabilityScore: 8 },
            { date: "02-15", dominantMood: "frustrated", spikeCount: 2, stabilityScore: 4 },
            { date: "02-16", dominantMood: "engaged", spikeCount: 0, stabilityScore: 9 },
            { date: "02-17", dominantMood: "anxious", spikeCount: 1, stabilityScore: 5 },
            { date: "02-18", dominantMood: "joyful", spikeCount: 0, stabilityScore: 10 },
            { date: "02-19", dominantMood: "frustrated", spikeCount: 3, stabilityScore: 3 },
            { date: "02-20", dominantMood: "engaged", spikeCount: 0, stabilityScore: 8 },
        ],
        recentSpikes: [
            { timestamp: "2026-02-19 14:30", conceptId: "Fractions", streakLength: 4, resolvedStatus: "RESOLVED" },
            { timestamp: "2026-02-19 15:10", conceptId: "Social Cues", streakLength: 3, resolvedStatus: "ACTIVE" },
        ]
    });

    return (
        <div className="space-y-6">
            <header className="mb-8">
                <h1 className="text-2xl font-bold text-white tracking-tight">Emotional Stability</h1>
                <p className="text-slate-400 mt-1">Monitoring frustration volatility and baseline recovery latencies.</p>
            </header>

            {/* Metric Cards Row */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Volatility Index</h3>
                        <div className="p-2 bg-orange-500/10 rounded-lg text-orange-400"><Activity size={20} /></div>
                    </div>
                    <div className="flex items-baseline">
                        <span className="text-3xl font-bold text-white">{data.emotionalVolatilityIndex}</span>
                        <span className="text-slate-400 ml-2 text-sm">score</span>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Recovery Latency</h3>
                        <div className="p-2 bg-blue-500/10 rounded-lg text-blue-400"><Clock size={20} /></div>
                    </div>
                    <div className="flex items-baseline">
                        <span className="text-3xl font-bold text-white">{data.avgRecoveryLatencyMinutes}</span>
                        <span className="text-slate-400 ml-2 text-sm">min / spike</span>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Resilience Growth</h3>
                        <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400"><ShieldAlert size={20} /></div>
                    </div>
                    <div className="flex items-baseline">
                        <span className="text-3xl font-bold text-white">+{((data.resilienceGrowthIndex - 1) * 100).toFixed(0)}%</span>
                        <span className="text-slate-400 ml-2 text-sm">since last month</span>
                    </div>
                </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Latency Recovery Trend / Stability Area */}
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 lg:col-span-2">
                    <h3 className="text-lg font-semibold text-white mb-6">Stability Trend Over Time</h3>
                    <div className="h-72 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={data.heatmapCalendar}>
                                <defs>
                                    <linearGradient id="colorStability" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={[0, 10]} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }}
                                    itemStyle={{ color: '#f1f5f9' }}
                                />
                                <Area type="monotone" dataKey="stabilityScore" stroke="#10b981" fillOpacity={1} fill="url(#colorStability)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Frustration Spike Alerts Panel */}
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col">
                    <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                        <AlertTriangle className="text-rose-500" size={20} />
                        Recent Alerts
                    </h3>
                    <div className="flex-1 overflow-y-auto space-y-4">
                        {data.recentSpikes.map((spike, i) => (
                            <div key={i} className={`p-4 rounded-lg border ${spike.resolvedStatus === 'ACTIVE' ? 'bg-rose-500/10 border-rose-500/20' : 'bg-gray-900 border-gray-700'}`}>
                                <div className="flex justify-between items-start mb-2">
                                    <span className={`text-xs font-semibold px-2 py-1 rounded full ${spike.resolvedStatus === 'ACTIVE' ? 'bg-rose-500/20 text-rose-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                                        {spike.resolvedStatus}
                                    </span>
                                    <span className="text-xs text-slate-500">{spike.timestamp}</span>
                                </div>
                                <h4 className="text-sm font-medium text-slate-200">Context: {spike.conceptId}</h4>
                                <p className="text-xs text-slate-400 mt-1">Duration streak: <span className="font-semibold text-rose-400">{spike.streakLength} turns</span></p>
                            </div>
                        ))}
                    </div>
                </div>

            </div>

            {/* Heatmap (Mocked via BarChart) */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">Mood Calendar Heatmap (Mocked)</h3>
                <div className="h-48 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data.heatmapCalendar}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                            <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis hide />
                            <Tooltip cursor={{ fill: '#334155', opacity: 0.4 }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
                            <Bar dataKey="spikeCount" name="Frustration Spikes">
                                {
                                    data.heatmapCalendar.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.spikeCount > 1 ? '#ef4444' : entry.spikeCount === 1 ? '#f59e0b' : '#334155'} />
                                    ))
                                }
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </div>

        </div>
    );
};

export default Emotions;
