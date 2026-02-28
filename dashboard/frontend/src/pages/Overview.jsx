import React, { useState, useEffect } from 'react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis,
    ScatterChart, Scatter, ZAxis
} from 'recharts';
import { Target, TrendingUp, Zap, Info } from 'lucide-react';

const Overview = () => {
    // Mocking the ZpdOverviewDto from Spring Boot for development scaffolding
    const [data, setData] = useState({
        currentAdvancementVelocity: 2.4,
        averageElasticityScore: 85.2,
        historicalTrends: [
            { timestamp: "Mon", successRate: 65, engagementFrequency: 4, difficultyMA: 3 },
            { timestamp: "Tue", successRate: 58, engagementFrequency: 6, difficultyMA: 4 },
            { timestamp: "Wed", successRate: 72, engagementFrequency: 3, difficultyMA: 3 },
            { timestamp: "Thu", successRate: 81, engagementFrequency: 8, difficultyMA: 5 },
            { timestamp: "Fri", successRate: 85, engagementFrequency: 5, difficultyMA: 6 },
        ],
        conceptMastery: [
            { conceptId: "Phonics", masteryScore: 90, totalAttempts: 12 },
            { conceptId: "Math", masteryScore: 65, totalAttempts: 8 },
            { conceptId: "Social", masteryScore: 85, totalAttempts: 20 },
            { conceptId: "Logic", masteryScore: 40, totalAttempts: 5 },
            { conceptId: "Verbal", masteryScore: 75, totalAttempts: 15 },
        ],
        // Enhancement 9: Cognitive Load Reduction Summary
        cognitiveSummary: {
            dominantRiskTrend: "Session trajectory is stable and tracking nominally.",
            recommendedAction: "Maintain current scaffolding and ZPD progression zones.",
            confidenceLevel: "High",
            structuredShortSummary: "Session trajectory is stable and tracking nominally. Maintain current scaffolding and ZPD progression zones. Confidence is high. Predictions fall cleanly within a tight 15% uncertainty margin."
        }
    });

    return (
        <div className="space-y-6">
            <header className="mb-8">
                <h1 className="text-2xl font-bold text-white tracking-tight">Educational Progress & ZPD</h1>
                <p className="text-slate-400 mt-1">Zone of Proximal Development metrics and cognitive mastery trends.</p>
            </header>

            {/* Cognitive Summary Banner */}
            <div className="bg-primary-900/20 border border-primary-500/30 rounded-xl p-4 flex gap-4 items-start">
                <div className="p-2 bg-primary-500/20 rounded-lg text-primary-400 shrink-0">
                    <Info size={24} />
                </div>
                <div>
                    <h3 className="text-primary-300 font-semibold mb-1">Clinical AI Summary</h3>
                    <p className="text-slate-300 text-sm leading-relaxed">{data.cognitiveSummary.structuredShortSummary}</p>
                </div>
            </div>

            {/* Metric Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-medium text-slate-400">Advancement Velocity</h3>
                        <div className="p-2 bg-primary-500/10 rounded-lg text-primary-400"><TrendingUp size={20} /></div>
                    </div>
                    <div>
                        <span className="text-3xl font-bold text-white">{data.currentAdvancementVelocity}</span>
                        <span className="text-slate-400 ml-2 text-sm">levels / week</span>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-medium text-slate-400">ZPD Elasticity Score</h3>
                        <div className="p-2 bg-emerald-500/10 rounded-lg text-emerald-400"><Zap size={20} /></div>
                    </div>
                    <div>
                        <span className="text-3xl font-bold text-white">{data.averageElasticityScore}</span>
                        <span className="text-slate-400 ml-2 text-sm">/ 100</span>
                    </div>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 flex flex-col justify-between">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-sm font-medium text-slate-400">Active Concepts</h3>
                        <div className="p-2 bg-rose-500/10 rounded-lg text-rose-400"><Target size={20} /></div>
                    </div>
                    <div>
                        <span className="text-3xl font-bold text-white">{data.conceptMastery.length}</span>
                        <span className="text-slate-400 ml-2 text-sm">in learning zone</span>
                    </div>
                </div>
            </div>

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">

                {/* Success Rate Line Graph */}
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6">Success Rate vs Difficulty</h3>
                    <div className="h-72 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={data.historicalTrends}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis dataKey="timestamp" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis yAxisId="left" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }}
                                    itemStyle={{ color: '#f1f5f9' }}
                                />
                                <Line yAxisId="left" type="monotone" dataKey="successRate" stroke="#6366f1" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} name="Success %" />
                                <Line yAxisId="right" type="monotone" dataKey="difficultyMA" stroke="#ec4899" strokeWidth={3} borderDash={[5, 5]} dot={false} name="Difficulty Level" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Domain Radar Chart */}
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <h3 className="text-lg font-semibold text-white mb-6">Domain Radar (Mastery)</h3>
                    <div className="h-72 w-full flex justify-center">
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={data.conceptMastery}>
                                <PolarGrid stroke="#334155" />
                                <PolarAngleAxis dataKey="conceptId" tick={{ fill: '#94a3b8', fontSize: 12 }} />
                                <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                                <Radar name="Mastery Score" dataKey="masteryScore" stroke="#6366f1" fill="#6366f1" fillOpacity={0.4} />
                                <Tooltip contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

            </div>

            {/* Charts Row 2 */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                <h3 className="text-lg font-semibold text-white mb-6">ZPD Elasticity Scatter Plot (Success vs Engagement)</h3>
                <div className="h-80 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                        <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis type="number" dataKey="totalAttempts" name="Attempts" stroke="#94a3b8" tickLine={false} axisLine={false} />
                            <YAxis type="number" dataKey="masteryScore" name="Mastery" stroke="#94a3b8" tickLine={false} axisLine={false} />
                            <ZAxis type="category" dataKey="conceptId" name="Concept" />
                            <Tooltip cursor={{ strokeDasharray: '3 3' }} contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }} />
                            <Scatter name="Concepts" data={data.conceptMastery} fill="#818cf8" />
                        </ScatterChart>
                    </ResponsiveContainer>
                </div>
            </div>

        </div>
    );
};

export default Overview;
