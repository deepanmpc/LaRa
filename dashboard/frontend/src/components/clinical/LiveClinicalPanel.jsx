import React from 'react';
import { Activity, Brain, Target, HeartPulse, Zap, AlertTriangle } from 'lucide-react';

const LiveClinicalPanel = ({ isLoading, metrics }) => {

    // Spec: Subtle loading state (shimmer)
    if (isLoading) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 animate-pulse">
                <div className="flex justify-between items-center mb-6">
                    <div className="h-6 w-48 bg-slate-200 rounded"></div>
                    <div className="h-6 w-24 bg-slate-200 rounded-full"></div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                    {[1, 2, 3, 4, 5, 6].map(i => (
                        <div key={i} className="h-24 bg-slate-100 rounded-lg"></div>
                    ))}
                </div>
            </div>
        );
    }

    if (!metrics) return null;

    const cards = [
        { title: "Emotional State", value: metrics.emotionalState, icon: HeartPulse, color: "text-rose-500", bg: "bg-rose-50" },
        { title: "Volatility (60s)", value: metrics.shortWindowVolatility?.toFixed(2), icon: Activity, color: "text-amber-500", bg: "bg-amber-50" },
        { title: "Frustration Spikes", value: metrics.frustrationCount, icon: AlertTriangle, color: "text-red-500", bg: "bg-red-50" },
        { title: "Engagement", value: `${(metrics.engagementLevel * 100).toFixed(0)}%`, icon: Zap, color: "text-blue-500", bg: "bg-blue-50" },
        { title: "Active Concept", value: metrics.currentConcept, icon: Brain, color: "text-purple-500", bg: "bg-purple-50" },
        { title: "ZPD Position", value: metrics.zpdPosition?.toFixed(1), icon: Target, color: "text-teal-500", bg: "bg-teal-50" },
    ];

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-medium text-slate-800 flex items-center gap-2">
                    <Activity size={20} className="text-emerald-500" />
                    Live Clinical Snapshot
                </h2>
                {/* Spec: Subtle "Live Session Active" badge */}
                <span className="flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-700 text-xs font-semibold rounded-full border border-emerald-100">
                    <span className="relative flex h-2 w-2">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                    </span>
                    SESSION ACTIVE
                </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                {cards.map((card, idx) => (
                    <div key={idx} className={`${card.bg} rounded-lg p-4 border border-white/50 shadow-sm relative overflow-hidden group`}>
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs font-medium text-slate-500 uppercase tracking-wider">{card.title}</span>
                            <card.icon size={16} className={card.color} />
                        </div>
                        <div className="text-xl font-bold text-slate-800">{card.value || '—'}</div>
                    </div>
                ))}
            </div>

            <p className="text-xs text-slate-400 mt-4 flex justify-end">
                Updated: {new Date(metrics.timestamp).toLocaleTimeString()}
            </p>
        </div>
    );
};

export default LiveClinicalPanel;
