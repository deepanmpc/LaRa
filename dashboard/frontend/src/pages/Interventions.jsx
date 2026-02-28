import React, { useState } from 'react';
import {
    ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ZAxis
} from 'recharts';
import { Activity, ShieldAlert, Crosshair } from 'lucide-react';

const Interventions = () => {
    // Mocking ToolIntelligenceService response
    const [data] = useState({
        successRate: 0.72,
        dependencyRiskScore: 0.45,
        totalInterventions: 142,
        bubbleData: [
            { tool: "Deep Breathing", duration: 120, successRate: 85, usageCount: 45 },
            { tool: "Gentle Nudge", duration: 10, successRate: 60, usageCount: 60 },
            { tool: "Sensory Break", duration: 300, successRate: 95, usageCount: 15 },
            { tool: "Cognitive Reframing", duration: 60, successRate: 40, usageCount: 22 },
        ],
        // Extended Mock mapping ToolDecayMetrics (Enhancement 4)
        tableLogs: [
            { id: 1, trigger: "Frustration (Z-Score: 2.1)", tool: "Guided Breathing", outcome: "+1.5", status: "Success", decaySlope: -0.02, habituationRisk: 15, cooldown: 0 },
            { id: 2, trigger: "Silence > 15s", tool: "Gentle Nudge", outcome: "+0.8", status: "Moderate", decaySlope: -0.08, habituationRisk: 80, cooldown: 120 },
            { id: 3, trigger: "ZPD Plateau", tool: "Reduce Difficulty (-10%)", outcome: "N/A", status: "Pending", decaySlope: 0.01, habituationRisk: 0, cooldown: 0 },
        ]
    });

    return (
        <div className="space-y-6">
            <header className="mb-8">
                <h1 className="text-2xl font-bold text-white tracking-tight">Tool Intelligence</h1>
                <p className="text-slate-400 mt-1">Intervention efficacy and dependency risk metrics.</p>
            </header>

            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Total Interventions</h3>
                        <div className="p-2 bg-primary-500/10 rounded-lg text-primary-400"><Activity size={20} /></div>
                    </div>
                    <div>
                        <span className="text-3xl font-bold text-white">{data.totalInterventions}</span>
                        <span className="text-slate-400 ml-2 text-sm">deployed</span>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Overarching Success</h3>
                        <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400"><Crosshair size={20} /></div>
                    </div>
                    <div>
                        <span className="text-3xl font-bold text-white">{(data.successRate * 100).toFixed(1)}%</span>
                        <span className="text-slate-400 ml-2 text-sm">positive shift</span>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Dependency Risk</h3>
                        <div className="p-2 bg-rose-500/10 rounded-lg text-orange-400"><ShieldAlert size={20} /></div>
                    </div>
                    <div>
                        <span className="text-3xl font-bold text-white">{data.dependencyRiskScore.toFixed(2)}</span>
                        <span className="text-slate-400 ml-2 text-sm">warning threshold &gt; 0.6</span>
                    </div>
                </div>
            </div>

            {/* Bubble Chart */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">Tool Effectiveness vs Duration (Bubble Size = Frequency)</h3>
                <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis type="number" dataKey="duration" name="Duration (s)" stroke="#94a3b8" tickLine={false} axisLine={false} />
                            <YAxis type="number" dataKey="successRate" name="Success %" stroke="#94a3b8" tickLine={false} axisLine={false} />
                            <ZAxis type="number" dataKey="usageCount" range={[100, 1000]} name="Usage Count" />
                            <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
                            <Scatter name="Tools" data={data.bubbleData} fill="#ec4899" opacity={0.8} />
                        </ScatterChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Advanced Datatable */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden mt-6">
                <div className="p-6 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-white">Recent Intervention Logs</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-300">
                        <thead className="bg-gray-700/50 text-slate-200">
                            <tr>
                                <th className="px-6 py-4 font-medium rounded-tl-lg">Trigger Condition</th>
                                <th className="px-6 py-4 font-medium">Intervention Tool deployed</th>
                                <th className="px-6 py-4 font-medium">Outcome Delta</th>
                                <th className="px-6 py-4 font-medium">Effectiveness Decay</th>
                                <th className="px-6 py-4 font-medium rounded-tr-lg">Efficacy Status</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700/50">
                            {data.tableLogs.map((row) => (
                                <tr key={row.id} className="hover:bg-gray-700/30 transition-colors">
                                    <td className="px-6 py-4 font-medium text-slate-200">{row.trigger}</td>
                                    <td className="px-6 py-4">{row.tool}</td>
                                    <td className="px-6 py-4">
                                        <span className={row.outcome.startsWith('+') ? 'text-emerald-400' : 'text-slate-400'}>
                                            {row.outcome}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4">
                                        {row.habituationRisk > 60 ? (
                                            <div className="flex flex-col gap-1">
                                                <span className="text-rose-400 flex items-center gap-1"><ShieldAlert size={14} /> Habituation Risk ({row.habituationRisk}%)</span>
                                                <span className="text-xs text-rose-500/70">Cooldown: {row.cooldown}m</span>
                                            </div>
                                        ) : (
                                            <span className="text-emerald-400">Stable (Slope: {row.decaySlope})</span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium 
                                            ${row.status === 'Success' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' :
                                                row.status === 'Moderate' ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20' :
                                                    'bg-gray-500/10 text-gray-400 border border-gray-500/20'}`}>
                                            {row.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    );
};

export default Interventions;
