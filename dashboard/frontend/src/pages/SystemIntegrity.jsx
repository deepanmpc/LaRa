import React, { useState } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts';
import { ShieldCheck, ServerCrash, AlertTriangle, Download } from 'lucide-react';

const SystemIntegrity = () => {
    // Mocking SystemIntegrityDto and OverrideLog payloads
    const [data] = useState({
        confidenceDecayRate: 0.04,
        distributionDriftMagnitude: 1.12,
        recentOverridesLimitSpike: 15,
        integrityStatus: "WARNING_DRIFT",
        driftHistory: [
            { day: "-14d", driftScore: 0.8 },
            { day: "-10d", driftScore: 0.9 },
            { day: "-7d", driftScore: 1.05 },
            { day: "-3d", driftScore: 1.15 },
            { day: "Today", driftScore: 1.12 },
        ],
        // Enhancements 1 & 8: Statistical Calibration & Bias Fairness
        calibration: {
            brierScore: 0.14,
            expectedCalibrationError: 0.06,
            overallReliability: "HIGH"
        },
        biasFairness: {
            riskScoreVarianceIndex: 0.04,
            fairnessStatus: "EQUITABLE"
        }
    });

    const getStatusTheme = (status) => {
        if (status === "CRITICAL_DECAY") return { color: "text-rose-500", bg: "bg-rose-500/10", border: "border-rose-500/30", icon: <ServerCrash size={24} /> };
        if (status === "WARNING_DRIFT") return { color: "text-orange-500", bg: "bg-orange-500/10", border: "border-orange-500/30", icon: <AlertTriangle size={24} /> };
        return { color: "text-emerald-500", bg: "bg-emerald-500/10", border: "border-emerald-500/30", icon: <ShieldCheck size={24} /> };
    };

    const theme = getStatusTheme(data.integrityStatus);

    return (
        <div className="space-y-6">
            <header className="mb-8 flex justify-between items-end">
                <div>
                    <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                        <ShieldCheck className="text-primary-400" /> System Integrity & Audit
                    </h1>
                    <p className="text-slate-400 mt-1">Monitoring global AI model drift, confidence decay, and compliance logs.</p>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-500 text-white font-medium rounded-lg transition-colors">
                    <Download size={16} /> Export Compliance CSV
                </button>
            </header>

            {/* Top Level Severity Banner */}
            <div className={`p-4 rounded-xl border flex items-center gap-4 ${theme.bg} ${theme.border} ${theme.color}`}>
                <div className="shrink-0">{theme.icon}</div>
                <div>
                    <h3 className="font-bold text-sm uppercase tracking-wider">System Status: {data.integrityStatus.replace('_', ' ')}</h3>
                    <p className="text-sm opacity-90 mt-1">Monitoring active divergence from validated baselines.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-sm font-medium text-slate-400 mb-2">Confidence Decay Rate</h3>
                        <div className="flex items-baseline">
                            <span className="text-3xl font-bold text-white">{(data.confidenceDecayRate * 100).toFixed(1)}%</span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-sm font-medium text-slate-400 mb-2">Expected Calibration Error (ECE)</h3>
                        <div className="flex items-baseline">
                            <span className="text-3xl font-bold text-emerald-400">{(data.calibration.expectedCalibrationError * 100).toFixed(1)}%</span>
                            <span className="text-slate-500 text-sm ml-2">reliability</span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-sm font-medium text-slate-400 mb-2">Brier Score (MSE)</h3>
                        <div className="flex items-baseline">
                            <span className="text-3xl font-bold text-white">{data.calibration.brierScore.toFixed(3)}</span>
                            <span className="text-slate-500 text-sm ml-2">closer to 0 is better</span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-sm font-medium text-slate-400 mb-2">KL Distribution Drift</h3>
                        <div className="flex items-baseline">
                            <span className="text-3xl font-bold text-white">{data.distributionDriftMagnitude.toFixed(2)}</span>
                            <span className="text-slate-500 text-sm ml-2">thresh &gt; 1.0</span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-sm font-medium text-slate-400 mb-2">Overall Subgroup Fairness Variance</h3>
                        <div className="flex items-baseline">
                            <span className="text-3xl font-bold text-emerald-400">{(data.biasFairness.riskScoreVarianceIndex * 100).toFixed(1)}%</span>
                            <span className="text-slate-500 text-sm ml-2 uppercase truncate">{data.biasFairness.fairnessStatus}</span>
                        </div>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div>
                        <h3 className="text-sm font-medium text-slate-400 mb-2">14-Day Override Spikes</h3>
                        <div className="flex items-baseline">
                            <span className="text-3xl font-bold text-rose-400">+{data.recentOverridesLimitSpike}</span>
                            <span className="text-slate-500 text-sm ml-2">vs prior period</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Distribution Drift Line Chart */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">Distribution Drift (Kullback-Leibler Divergence)</h3>
                <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={data.driftHistory}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                            <XAxis dataKey="day" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                            <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={[0, 2]} />
                            <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
                            <ReferenceLine y={1.0} stroke="#f59e0b" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Warning Threshold', fill: '#f59e0b', fontSize: 12 }} />
                            <ReferenceLine y={1.5} stroke="#ef4444" strokeDasharray="3 3" label={{ position: 'insideTopLeft', value: 'Critical Threshold', fill: '#ef4444', fontSize: 12 }} />
                            <Line type="monotone" dataKey="driftScore" stroke="#818cf8" strokeWidth={3} dot={{ r: 4 }} name="Drift Magnitude" />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>

            {/* Compliance Log Table */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl overflow-hidden mt-6">
                <div className="p-6 border-b border-gray-700">
                    <h3 className="text-lg font-semibold text-white">System Override Audit Trail</h3>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm text-slate-400">
                        <thead className="bg-gray-900/50 text-xs uppercase bg-gray-900 border-b border-gray-700">
                            <tr>
                                <th className="px-6 py-4">Timestamp (UTC)</th>
                                <th className="px-6 py-4">Severity</th>
                                <th className="px-6 py-4">AI Trigger</th>
                                <th className="px-6 py-4">Overridden To</th>
                                <th className="px-6 py-4">Clinician</th>
                                <th className="px-6 py-4">Required Rationale</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-700">
                            {data.auditLogs.map((log, i) => (
                                <tr key={i} className="hover:bg-gray-700/50 transition-colors">
                                    <td className="px-6 py-4 font-mono text-slate-500 text-xs">{log.timestamp}</td>
                                    <td className="px-6 py-4">
                                        <span className={`px-2 py-1 rounded text-xs font-bold ${log.severity === 'HIGH' ? 'bg-rose-500/10 text-rose-500' :
                                            log.severity === 'MED' ? 'bg-orange-500/10 text-orange-500' :
                                                'bg-emerald-500/10 text-emerald-500'
                                            }`}>{log.severity}</span>
                                    </td>
                                    <td className="px-6 py-4 text-slate-300">{log.aiDecision}</td>
                                    <td className="px-6 py-4 font-medium text-white">{log.overriddenTo}</td>
                                    <td className="px-6 py-4 text-slate-400">{log.clinicianId}</td>
                                    <td className="px-6 py-4 italic text-slate-500">"{log.rationale}"</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

        </div>
    );
};

export default SystemIntegrity;
