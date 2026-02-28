import React, { useState } from 'react';
import { Play, Settings2, ShieldAlert } from 'lucide-react';
import {
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ErrorBar
} from 'recharts';

const SimulationSandbox = () => {
    const [difficultyOffset, setDifficultyOffset] = useState(0);
    const [interventionOffset, setInterventionOffset] = useState(0);

    // Mock Payload simulating output from `POST /api/simulate/{userId}`
    const [simulationData, setSimulationData] = useState({
        isSimulated: true, // Flag enforcing visual discrepancy from true data
        frustrationRisk: { val: 65, errorWidth: 15 },
        masteryStagnation: { val: 40, errorWidth: 10 },
        independenceScore: { val: 70, errorWidth: 20 }
    });

    const handleSimulate = () => {
        // Mocking the elasticity logic to update the local graph projections
        const diffAdj = difficultyOffset / 100.0;
        const intAdj = interventionOffset / 100.0;

        const newFrust = Math.max(0, Math.min(100, 65 + (diffAdj * 80) - (intAdj * 40)));
        const newStag = Math.max(0, Math.min(100, 40 - (diffAdj * 50)));
        const newIndep = Math.max(0, Math.min(100, 70 - (intAdj * 60) + (diffAdj * 20)));

        const widthMult = 1.0 + Math.abs(diffAdj) + Math.abs(intAdj);

        setSimulationData({
            isSimulated: true,
            frustrationRisk: { val: newFrust, errorWidth: 15 * widthMult },
            masteryStagnation: { val: newStag, errorWidth: 10 * widthMult },
            independenceScore: { val: newIndep, errorWidth: 20 * widthMult }
        });
    };

    // Reformatting for Recharts ErrorBar component
    const chartData = [
        { name: 'Frustration Escalation', value: simulationData.frustrationRisk.val, error: [simulationData.frustrationRisk.errorWidth, simulationData.frustrationRisk.errorWidth] },
        { name: 'Mastery Stagnation', value: simulationData.masteryStagnation.val, error: [simulationData.masteryStagnation.errorWidth, simulationData.masteryStagnation.errorWidth] },
        { name: 'Independence Level', value: simulationData.independenceScore.val, error: [simulationData.independenceScore.errorWidth, simulationData.independenceScore.errorWidth] }
    ];

    return (
        <div className="space-y-6">
            <header className="mb-8">
                <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                    <Settings2 className="text-amber-500" /> Counterfactual Sandbox
                </h1>
                <p className="text-slate-400 mt-1">Project non-observed risk margins based on simulated clinical adjustments.</p>
            </header>

            <div className="p-4 rounded-xl border border-amber-500/30 bg-amber-500/10 text-amber-500 flex items-center gap-4">
                <ShieldAlert size={24} className="shrink-0" />
                <div>
                    <h3 className="font-bold text-sm uppercase tracking-wider">Simulated Projection – Not Observed Data</h3>
                    <p className="text-sm opacity-90 mt-1">Error margins widen substantially as derived projections stray from actual historic elasticity.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* Control Panel */}
                <div className="lg:col-span-1 space-y-6 bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-4">Intervention Dials</h3>

                    <div>
                        <div className="flex justify-between mb-2">
                            <label className="text-sm font-medium text-slate-300">Difficulty Bias</label>
                            <span className="text-sm text-amber-400 font-mono">{difficultyOffset > 0 ? '+' : ''}{difficultyOffset}%</span>
                        </div>
                        <input type="range" min="-30" max="30" value={difficultyOffset} onChange={(e) => setDifficultyOffset(Number(e.target.value))} className="w-full accent-amber-500" />
                        <p className="text-xs text-slate-500 mt-1">Adjust aggregate task difficulty level</p>
                    </div>

                    <div>
                        <div className="flex justify-between mb-2">
                            <label className="text-sm font-medium text-slate-300">Intervention Frequency</label>
                            <span className="text-sm text-amber-400 font-mono">{interventionOffset > 0 ? '+' : ''}{interventionOffset}%</span>
                        </div>
                        <input type="range" min="-50" max="50" value={interventionOffset} onChange={(e) => setInterventionOffset(Number(e.target.value))} className="w-full accent-amber-500" />
                        <p className="text-xs text-slate-500 mt-1">Force heavier scaffolding or extreme fading.</p>
                    </div>

                    <button onClick={handleSimulate} className="w-full flex justify-center items-center gap-2 px-4 py-3 bg-amber-600 hover:bg-amber-500 text-white font-bold rounded-lg transition-colors mt-8">
                        <Play size={18} /> Update Projection Model
                    </button>
                </div>

                {/* Counterfactual Projection Visuals */}
                <div className="lg:col-span-2 bg-gray-900 border border-gray-700/50 rounded-xl p-6 shadow-inner relative overflow-hidden">
                    <div className="absolute inset-0 bg-amber-900/5 pointer-events-none"></div> {/* Visual disclaimer wash */}
                    <h3 className="text-lg font-semibold text-slate-200 mb-6">Derived Outcome Probability</h3>

                    <div className="h-72 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#f59e0b', borderRadius: '8px', color: '#f1f5f9' }}
                                    formatter={(value, name, props) => {
                                        const err = props.payload.error[0].toFixed(1);
                                        return [`${value.toFixed(1)}% (±${err}%)`, name];
                                    }}
                                />
                                <Bar dataKey="value" fill="#f59e0b" radius={[4, 4, 0, 0]}>
                                    <ErrorBar dataKey="error" width={4} strokeWidth={2} stroke="#fcd34d" direction="y" />
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default SimulationSandbox;
