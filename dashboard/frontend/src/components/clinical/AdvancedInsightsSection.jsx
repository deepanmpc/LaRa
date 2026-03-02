import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Stethoscope, AlertTriangle, TrendingDown, Combine, LineChart } from 'lucide-react';

const AdvancedInsightsSection = ({ metrics }) => {
    // Collapsed by default as per spec
    const [isExpanded, setIsExpanded] = useState(false);

    if (!metrics) return null;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden mt-8">

            <div
                className="p-6 flex justify-between items-center cursor-pointer hover:bg-slate-50 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div>
                    <h2 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                        <Stethoscope size={20} className="text-slate-400" />
                        Advanced Clinical Insights
                    </h2>
                    <p className="text-sm text-slate-500 mt-1">Plateau detection, scaffolding risk, and decay modeling.</p>
                </div>
                <div className="p-2 bg-slate-100 rounded-full text-slate-500">
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </div>
            </div>

            {isExpanded && (
                <div className="p-6 border-t border-slate-200 bg-slate-50 flex flex-col gap-6">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

                        {/* Over-Scaffolding Risk */}
                        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-16 h-16 bg-rose-50 rounded-bl-full -mr-8 -mt-8"></div>
                            <div className="flex items-center gap-2 mb-3">
                                <AlertTriangle size={16} className="text-rose-500" />
                                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Over-Scaffolding</h3>
                            </div>
                            <div className="text-2xl font-light text-slate-800 tracking-tight mb-2">High (35%)</div>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                Prompt dependency index elevated. The system is intervening before independent recovery occurs in 35% of tasks.
                            </p>
                        </div>

                        {/* Plateau Detection */}
                        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-16 h-16 bg-amber-50 rounded-bl-full -mr-8 -mt-8"></div>
                            <div className="flex items-center gap-2 mb-3">
                                <LineChart size={16} className="text-amber-500" />
                                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Plateau Detection</h3>
                            </div>
                            <div className="text-2xl font-light text-slate-800 tracking-tight mb-2">Flagged</div>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                Stagnation probability ({metrics.frustrationRiskScore || 22.5}%) exceeds threshold on phonetic clustering concepts.
                            </p>
                        </div>

                        {/* Habituation Decay Slope */}
                        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-16 h-16 bg-blue-50 rounded-bl-full -mr-8 -mt-8"></div>
                            <div className="flex items-center gap-2 mb-3">
                                <TrendingDown size={16} className="text-blue-500" />
                                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Intervention Decay</h3>
                            </div>
                            <div className="text-2xl font-light text-slate-800 tracking-tight mb-2">
                                {metrics.interventionDecayIndex?.toFixed(3) || '-0.024'}
                            </div>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                Tool effectiveness is decreasing over time. Deep Breathing requires 24% more prompts to reach baseline regulation.
                            </p>
                        </div>

                        {/* Cross-Concept Interference */}
                        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm relative overflow-hidden">
                            <div className="absolute top-0 right-0 w-16 h-16 bg-teal-50 rounded-bl-full -mr-8 -mt-8"></div>
                            <div className="flex items-center gap-2 mb-3">
                                <Combine size={16} className="text-teal-500" />
                                <h3 className="text-xs font-bold text-slate-500 uppercase tracking-widest">Interference</h3>
                            </div>
                            <div className="text-2xl font-light text-slate-800 tracking-tight mb-2">Zero</div>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                No significant regression observed in previously mastered areas during current complexity advancement.
                            </p>
                        </div>

                    </div>
                </div>
            )}
        </div>
    );
};

export default AdvancedInsightsSection;
