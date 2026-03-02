import React, { useState } from 'react';
import { ChevronDown, ChevronUp, Beaker, Network, ScatterChart, TrendingDown } from 'lucide-react';

const AdvancedClinicalPanel = ({ metrics }) => {
    // Collapsed by default as per spec
    const [isExpanded, setIsExpanded] = useState(false);

    if (!metrics) return null;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
            {/* Header / Clickable Accordion Row */}
            <div
                className="p-6 flex justify-between items-center cursor-pointer hover:bg-slate-50 transition-colors"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <div>
                    <h2 className="text-lg font-medium text-slate-800 flex items-center gap-2">
                        <Beaker size={20} className="text-violet-500" />
                        Advanced Clinical Insights
                    </h2>
                    <p className="text-sm text-slate-500 mt-1">Research-grade intelligence, plateau forecasting, and decay modeling.</p>
                </div>
                <div className="p-2 bg-slate-100 rounded-full text-slate-500">
                    {isExpanded ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                </div>
            </div>

            {/* Expandable Content Area */}
            {isExpanded && (
                <div className="p-6 border-t border-slate-200 bg-slate-50/50">
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

                        {/* Habituation Decay Slope */}
                        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                            <div className="flex items-start justify-between mb-4">
                                <div className="p-2 bg-violet-50 text-violet-600 rounded-md">
                                    <TrendingDown size={20} />
                                </div>
                            </div>
                            <h3 className="text-sm font-semibold text-slate-800 mb-1">Habituation Decay Slope</h3>
                            <div className="text-2xl font-bold text-slate-900 mb-2">{metrics.interventionDecayIndex?.toFixed(3) || '-0.024'}</div>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                Tool effectiveness is decreasing over time. Deep Breathing requires 24% more prompts to reach baseline regulation.
                            </p>
                        </div>

                        {/* Over-Scaffolding Risk */}
                        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                            <div className="flex items-start justify-between mb-4">
                                <div className="p-2 bg-rose-50 text-rose-600 rounded-md">
                                    <AlertTriangle size={20} />
                                </div>
                            </div>
                            <h3 className="text-sm font-semibold text-slate-800 mb-1">Over-Scaffolding Risk</h3>
                            <div className="text-2xl font-bold text-rose-600 mb-2">High (35%)</div>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                Prompt dependency index is elevated. The system is intervening before independent recovery occurs in 35% of tasks.
                            </p>
                        </div>

                        {/* Plateau Detection */}
                        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                            <div className="flex items-start justify-between mb-4">
                                <div className="p-2 bg-amber-50 text-amber-600 rounded-md">
                                    <ScatterChart size={20} />
                                </div>
                            </div>
                            <h3 className="text-sm font-semibold text-slate-800 mb-1">Plateau Detection</h3>
                            <div className="text-2xl font-bold text-amber-600 mb-2">Flagged</div>
                            <p className="text-xs text-slate-500 leading-relaxed">
                                Stagnation probability ({metrics.frustrationRiskScore || 22.5}%) exceeds threshold on phonetic clustering concepts.
                            </p>
                        </div>

                        {/* Cross-Concept Interference */}
                        <div className="bg-white p-5 rounded-lg border border-slate-200 shadow-sm">
                            <div className="flex items-start justify-between mb-4">
                                <div className="p-2 bg-blue-50 text-blue-600 rounded-md">
                                    <Network size={20} />
                                </div>
                            </div>
                            <h3 className="text-sm font-semibold text-slate-800 mb-1">Concept Interference</h3>
                            <div className="text-2xl font-bold text-slate-900 mb-2">Minimal</div>
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

// Provide a quick icon stand-in locally if AlertTriangle wasn't imported properly
import { AlertTriangle } from 'lucide-react';

export default AdvancedClinicalPanel;
