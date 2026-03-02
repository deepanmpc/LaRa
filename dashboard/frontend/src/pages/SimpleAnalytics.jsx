import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Sparkles, HeartPulse, ShieldCheck, TrendingUp, CheckCircle2, ArrowUpRight, ArrowRight, ArrowDownRight } from 'lucide-react';

const API_BASE = 'http://localhost:8080/api/analytics/simple';

const SimpleAnalytics = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetching with a mock student ID for dev display
        const fetchSimpleData = async () => {
            try {
                const res = await axios.get(`${API_BASE}/mock-student-id`);
                setData(res.data);
                setLoading(false);
            } catch (err) {
                console.error("Failed to load caregiver analytics", err);
                setLoading(false);
            }
        };
        fetchSimpleData();
    }, []);

    if (loading) return (
        <div className="flex h-full items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-500"></div>
        </div>
    );

    if (!data) return <div>Failed to load data.</div>;

    const { sessionSummary, emotionalOverview, interventionSummary, progressSnapshot } = data;

    const renderTrendIcon = (trend) => {
        switch (trend) {
            case 'UP': return <ArrowUpRight className="text-emerald-500" size={20} />;
            case 'STABLE': return <ArrowRight className="text-blue-500" size={20} />;
            case 'DOWN': return <ArrowDownRight className="text-rose-500" size={20} />;
            default: return null;
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-fade-in-up pb-12">

            {/* Header Narrative */}
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100 flex items-start gap-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
                    <Sparkles className="text-blue-500" size={32} />
                </div>
                <div>
                    <h2 className="text-2xl font-extrabold text-slate-800 mb-2">Today's Summary</h2>
                    <p className="text-slate-600 text-lg leading-relaxed">
                        Today focused on <span className="font-bold text-blue-600">{sessionSummary.learningFocus}</span>.
                        Overall, emotional stability remained <span className="font-bold text-emerald-600">{sessionSummary.emotionalStabilityStatus}</span> throughout the session.
                    </p>
                    <div className="mt-4 flex gap-2 flex-wrap">
                        {sessionSummary.conceptsMastered.map((c, i) => (
                            <span key={i} className="inline-flex items-center gap-1 px-4 py-2 bg-emerald-50 text-emerald-700 rounded-full text-sm font-bold border border-emerald-100">
                                <CheckCircle2 size={16} /> Mastered: {c}
                            </span>
                        ))}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* Emotional Overview */}
                <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100">
                    <div className="flex items-center gap-3 mb-6">
                        <HeartPulse className="text-rose-500" size={28} />
                        <h3 className="text-xl font-bold text-slate-800">Emotional Wellbeing</h3>
                    </div>
                    <ul className="space-y-6">
                        <li className="flex justify-between items-center pb-4 border-b border-slate-50">
                            <span className="text-slate-600 font-medium">Recovery Speed</span>
                            <span className="px-4 py-1.5 bg-emerald-100 text-emerald-700 font-bold rounded-full text-sm">{emotionalOverview.recoverySpeed}</span>
                        </li>
                        <li className="flex justify-between items-center pb-4 border-b border-slate-50">
                            <span className="text-slate-600 font-medium">Moments of Frustration</span>
                            <span className="px-4 py-1.5 bg-blue-100 text-blue-700 font-bold rounded-full text-sm">{emotionalOverview.frustrationSpikes}</span>
                        </li>
                        <li className="flex justify-between items-center pb-4 border-b border-slate-50">
                            <span className="text-slate-600 font-medium">Weekly Trend</span>
                            <span className="text-slate-800 font-bold">{emotionalOverview.weekOverWeekTrend}</span>
                        </li>
                    </ul>
                </div>

                {/* Intervention Summary */}
                <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100">
                    <div className="flex items-center gap-3 mb-6">
                        <ShieldCheck className="text-purple-500" size={28} />
                        <h3 className="text-xl font-bold text-slate-800">How LaRa Helped</h3>
                    </div>
                    <div className="space-y-4">
                        <div className="p-4 bg-purple-50 border border-purple-100 rounded-2xl">
                            <p className="text-purple-900 font-medium">{interventionSummary.primaryToolEffectiveness}</p>
                        </div>
                        <div className="p-4 bg-blue-50 border border-blue-100 rounded-2xl">
                            <p className="text-blue-900 font-medium">{interventionSummary.secondaryToolEffectiveness}</p>
                        </div>
                        <div className="mt-6 pt-4 border-t border-slate-100">
                            <p className="text-slate-500 text-sm font-semibold uppercase tracking-wider mb-1">Recommendation</p>
                            <p className="text-slate-700 font-medium">{interventionSummary.generalRecommendation}</p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Progress Snapshot */}
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100">
                <div className="flex items-center gap-3 mb-8">
                    <TrendingUp className="text-emerald-500" size={28} />
                    <h3 className="text-xl font-bold text-slate-800">Learning Progress</h3>
                </div>
                <div className="space-y-6">
                    {progressSnapshot.map((concept, idx) => (
                        <div key={idx}>
                            <div className="flex justify-between items-end mb-2">
                                <span className="font-bold text-slate-700">{concept.conceptName}</span>
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-bold text-slate-500">{concept.masteryPercentage}%</span>
                                    {renderTrendIcon(concept.trend)}
                                </div>
                            </div>
                            <div className="w-full bg-slate-100 rounded-full h-3 overflow-hidden">
                                <div
                                    className={`h-3 rounded-full transition-all duration-1000 ${concept.masteryPercentage > 75 ? 'bg-emerald-400' : concept.masteryPercentage > 40 ? 'bg-blue-400' : 'bg-rose-400'}`}
                                    style={{ width: `${concept.masteryPercentage}%` }}
                                ></div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-8 pt-6 border-t border-slate-100 p-6 bg-blue-50 rounded-2xl">
                    <h4 className="font-bold text-blue-900 mb-2">Recommended Next Steps</h4>
                    <p className="text-blue-800 text-sm leading-relaxed pb-2">{sessionSummary.recommendedNextSteps}</p>
                </div>
            </div>

        </div>
    );
};

export default SimpleAnalytics;
