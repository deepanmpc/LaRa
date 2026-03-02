import React from 'react';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';

const ClinicalMetricCard = ({ title, value, trend, trendLabel, explanation, sparklineData }) => {

    // Determine trend visual styling
    let TrendIcon = Minus;
    let trendColor = "text-slate-400";
    let bgPulse = "";

    if (trend === 'up') {
        TrendIcon = TrendingUp;
        trendColor = "text-emerald-500";
        bgPulse = "bg-emerald-50 text-emerald-700 border-emerald-100";
    } else if (trend === 'down') {
        TrendIcon = TrendingDown;
        trendColor = "text-rose-500";
        bgPulse = "bg-rose-50 text-rose-700 border-rose-100";
    }

    return (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden group">

            <div className="flex justify-between items-start mb-2">
                <h3 className="text-sm font-semibold text-slate-600 tracking-tight">{title}</h3>
                <div className={`flex items-center gap-1 px-2 py-0.5 rounded-md text-[10px] font-bold border ${bgPulse}`}>
                    <TrendIcon size={12} strokeWidth={2.5} />
                    <span>{trendLabel}</span>
                </div>
            </div>

            <div className="text-3xl font-light text-slate-800 tracking-tight mb-3">
                {value}
            </div>

            <p className="text-xs text-slate-500 leading-relaxed border-t border-slate-50 pt-3">
                {explanation}
            </p>

            {/* Optional Sparkline decoration (Subtle CSS bar replacement for actual canvas graphs here) */}
            {sparklineData && (
                <div className="absolute bottom-0 left-0 w-full h-1 bg-slate-100 flex items-end">
                    {sparklineData.map((h, i) => (
                        <div key={i} style={{ height: `${h}%` }} className="flex-1 bg-blue-200 opacity-50 group-hover:bg-blue-400 transition-colors"></div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default ClinicalMetricCard;
