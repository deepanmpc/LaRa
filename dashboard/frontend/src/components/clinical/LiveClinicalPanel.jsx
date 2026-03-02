import React from 'react';
import { Activity, Brain, Target, HeartPulse, Zap, AlertTriangle } from 'lucide-react';

const LiveClinicalPanel = ({ isLoading, metrics }) => {

    // Spec: Subtle loading state (shimmer)
    if (isLoading) {
        return (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 animate-pulse">
                <div className="flex justify-between items-center mb-6">
                    <div className="h-4 w-48 bg-slate-200 rounded"></div>
                    <div className="h-4 w-24 bg-slate-200 rounded-full"></div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
                    {[1, 2, 3, 4, 5, 6].map(i => (
                        <div key={i} className="h-20 bg-slate-50 border border-slate-100 rounded-lg"></div>
                    ))}
                </div>
            </div>
        );
    }

    if (!metrics) return null;

    const cards = [
        { title: "Emotional State", value: metrics.emotionalState, icon: HeartPulse, color: "text-blue-500" },
        { title: "Volatility (60s)", value: metrics.shortWindowVolatility?.toFixed(2), icon: Activity, color: "text-blue-500" },
        { title: "Frustrations", value: metrics.frustrationCount, icon: AlertTriangle, color: "text-amber-500" },
        { title: "Engagement", value: `${(metrics.engagementLevel * 100).toFixed(0)}%`, icon: Zap, color: "text-emerald-500" },
        { title: "Active Concept", value: metrics.currentConcept, icon: Brain, color: "text-slate-500" },
        { title: "ZPD Position", value: metrics.zpdPosition?.toFixed(1), icon: Target, color: "text-slate-500" },
    ];

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
            <div className="flex justify-between items-center mb-6 border-b border-slate-100 pb-4">
                <h2 className="text-sm font-semibold text-slate-700 tracking-wider uppercase flex items-center gap-2">
                    <Activity size={16} className="text-blue-500" />
                    Live Session Metrics
                </h2>
                {/* Spec: Subtle "Live Session Active" badge via clean UI borders */}
                <span className="flex items-center gap-2 px-3 py-1 bg-white text-emerald-600 border border-emerald-200 text-xs font-bold tracking-widest rounded-full shadow-sm">
                    <span className="h-2 w-2 rounded-full bg-emerald-500"></span>
                    ACTIVE
                </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-6">
                {cards.map((card, idx) => (
                    <div key={idx} className="flex flex-col relative border-l-2 border-slate-100 pl-4 py-1">
                        <div className="flex items-center gap-2 mb-1">
                            <card.icon size={14} className={card.color} />
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{card.title}</span>
                        </div>
                        <div className="text-xl font-semibold text-slate-700 tracking-tight">{card.value || '—'}</div>
                    </div>
                ))}
            </div>

            <p className="text-[10px] text-slate-400 mt-6 text-right font-medium uppercase tracking-widest">
                Last Sync: {new Date(metrics.timestamp).toLocaleTimeString()}
            </p>
        </div>
    );
};

export default LiveClinicalPanel;
