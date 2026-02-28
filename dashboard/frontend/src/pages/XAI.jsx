import React, { useState } from 'react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    ComposedChart, Line
} from 'recharts';
import { BrainCircuit, Filter, HelpCircle } from 'lucide-react';

const XAI = () => {
    // Mocking AiConfidenceLog payload from Spring Boot
    const [data] = useState([
        { id: 1, triggerReason: "High Frustration Streak", aiConfidenceScore: Math.random() * 100, interventionProbability: 85, overrides: 0 },
        { id: 2, triggerReason: "Concept Mastery Velocity Drop", aiConfidenceScore: Math.random() * 100, interventionProbability: 40, overrides: 1 },
        { id: 3, triggerReason: "Silence Detected > 10s", aiConfidenceScore: Math.random() * 100, interventionProbability: 95, overrides: 0 },
        { id: 4, triggerReason: "Repeated Errors in Math", aiConfidenceScore: Math.random() * 100, interventionProbability: 60, overrides: 2 },
        { id: 5, triggerReason: "Sudden Joyful State", aiConfidenceScore: Math.random() * 100, interventionProbability: 10, overrides: 0 },
    ]);

    return (
        <div className="space-y-6">
            <header className="mb-8 flex justify-between items-end">
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                        <BrainCircuit className="text-primary-400" /> Explainable AI (XAI)
                    </h1>
                    <p className="text-slate-400 mt-1">Audit logs for autonomous LaRa decisions and clinician overrides.</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-slate-300 hover:text-white hover:bg-gray-700 transition-colors">
                    <Filter size={16} /> Filter Logs
                </button>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* AI Confidence Distribution */}
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-white">Confidence Distribution</h3>
                        <HelpCircle size={16} className="text-slate-500 hover:text-slate-300 cursor-pointer" />
                    </div>
                    <div className="h-72 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <ComposedChart data={data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis dataKey="triggerReason" stroke="#94a3b8" fontSize={10} tickFormatter={(tick) => tick.substring(0, 10) + "..."} tickLine={false} axisLine={false} />
                                <YAxis yAxisId="left" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }}
                                    itemStyle={{ color: '#f1f5f9' }}
                                />
                                <Bar yAxisId="left" dataKey="aiConfidenceScore" name="Confidence %" fill="#818cf8" radius={[4, 4, 0, 0]} />
                                <Line yAxisId="right" type="step" dataKey="interventionProbability" name="Act Probability %" stroke="#ec4899" strokeWidth={3} dot={false} />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Feature Attribution Bars */}
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6">SHAP Feature Attributions</h3>
                    <div className="space-y-4">
                        {[
                            { feature: 'Vocal Prosody (Anger)', weight: 0.85 },
                            { feature: 'Time Since Last Success', weight: 0.62 },
                            { feature: 'Concept ZPD Gap', weight: 0.45 },
                            { feature: 'Historical Tool Success', weight: 0.21 },
                        ].map((f, i) => (
                            <div key={i}>
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-200">{f.feature}</span>
                                    <span className="text-primary-400 font-mono">{(f.weight * 100).toFixed(1)}%</span>
                                </div>
                                <div className="w-full bg-gray-900 rounded-full h-2">
                                    <div className="bg-primary-500 h-2 rounded-full" style={{ width: `${f.weight * 100}%` }}></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>

            {/* Override Log Table */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden mt-6">
                <div className="p-6 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-white">Recent Clinician Overrides</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-400">
                        <thead className="bg-gray-900/50 text-xs uppercase bg-gray-900 border-b border-gray-700">
                            <tr>
                                <th className="px-6 py-4">Trigger Event</th>
                                <th className="px-6 py-4">AI Decision</th>
                                <th className="px-6 py-4">Overridden To</th>
                                <th className="px-6 py-4">Clinician Rationale</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700">
                            <tr className="hover:bg-gray-700/50 transition-colors">
                                <td className="px-6 py-4 font-medium text-slate-200">High Frustration</td>
                                <td className="px-6 py-4 text-emerald-400">Deep Breathing Tool</td>
                                <td className="px-6 py-4 text-rose-400">Therapist Takeover</td>
                                <td className="px-6 py-4">"Child escalates during breathing exercises."</td>
                            </tr>
                            <tr className="hover:bg-gray-700/50 transition-colors">
                                <td className="px-6 py-4 font-medium text-slate-200">Silence > 15s</td>
                                <td className="px-6 py-4 text-emerald-400">Gentle Nudge</td>
                                <td className="px-6 py-4 text-rose-400">Wait Longer</td>
                                <td className="px-6 py-4">"Processing delay, do not interrupt yet."</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    );
};

export default XAI;
