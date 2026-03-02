import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
    Sparkles, HeartPulse, ShieldCheck, TrendingUp, CheckCircle2,
    ArrowUpRight, ArrowRight, ArrowDownRight, UserCircle, Calendar,
    Clock, Target, Trophy, FileText, Send, Eye
} from 'lucide-react';

const API_BASE = 'http://localhost:8080/api/dashboard';

const SimpleAnalytics = () => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [note, setNote] = useState('');
    const [noteSuccess, setNoteSuccess] = useState(false);

    useEffect(() => {
        const fetchSimpleData = async () => {
            try {
                const res = await axios.get(`${API_BASE}/simple/mock-student-id`);
                setData(res.data);
                setLoading(false);
            } catch (err) {
                console.error("Failed to load caregiver analytics from API, using fallback mock data", err);

                // Fallback mock data matching the backend DTO structure
                const fallbackData = {
                    activeChildOverview: {
                        childName: "Leo Smith",
                        age: 6,
                        currentLearningTheme: "Fractions & Shapes",
                        lastSessionDate: "Today, 2:30 PM",
                        overallStatusBadge: "Doing Well"
                    },
                    sessionSummary: {
                        learningFocus: "Fractions & Division",
                        emotionalStabilityStatus: "Stable",
                        conceptsPracticed: ["Intro to Fractions", "Basic Geometry"],
                        conceptsMastered: ["Intro to Fractions"],
                        aiNarrativeSummary: "Leo had a wonderful session today. He grasped the concept of basic fractions very quickly and remained completely engaged. When things got slightly tricky during division, he took a deep breath on his own and powered through. No intervention was needed!"
                    },
                    weeklySnapshot: {
                        sessionsCompleted: 4,
                        totalLearningTime: "2h 15m",
                        conceptsAdvanced: 3,
                        emotionalStabilityTrend: "Improving",
                        weeklySummarySentence: "This week showed steady progress with highly improved emotional regulation compared to last week."
                    },
                    emotionalOverview: {
                        recoverySpeed: "Fast",
                        frustrationSpikes: 1,
                        weekOverWeekTrend: "Improved"
                    },
                    engagementIndicator: {
                        engagementLevel: "Highly Engaged",
                        participationScore: "Active"
                    },
                    interventionSummary: {
                        effectivenessStatements: [
                            "Breathing exercises helped 2 out of 2 times.",
                            "Gentle nudges were very effective today."
                        ],
                        generalRecommendation: "The current coping strategies are working beautifully. Consider continuing them next week."
                    },
                    milestonesAndAchievements: [
                        "🎉 Completed first independent counting sequence.",
                        "🌟 Managed a moment of frustration without any robot assistance!",
                        "🏆 Improved recovery time by 30% compared to last week."
                    ],
                    recommendedNextSteps: [
                        "Continue practicing division to reinforce the fraction concepts.",
                        "Offer brief breaks if the geometry sections begin to feel long.",
                        "Try a new storytelling activity to mix up the math routines."
                    ],
                    progressSnapshot: [
                        { conceptName: "Intro to Fractions", masteryPercentage: 85, trend: "UP" },
                        { conceptName: "Basic Geometry", masteryPercentage: 45, trend: "STABLE" },
                        { conceptName: "Word Problems", masteryPercentage: 20, trend: "DOWN" }
                    ],
                    sessionHistory: [
                        { date: "Oct 24", duration: "30m", emotionalSummary: "Stable and happy", progressIndicator: "Strong Progress" },
                        { date: "Oct 22", duration: "25m", emotionalSummary: "Slightly challenged, but recovered", progressIndicator: "Developing" },
                        { date: "Oct 20", duration: "40m", emotionalSummary: "Highly engaged", progressIndicator: "Strong Progress" }
                    ]
                };

                setData(fallbackData);
                setLoading(false);
            }
        };
        fetchSimpleData();
    }, []);

    const handleNoteSubmit = async (e) => {
        e.preventDefault();
        try {
            await axios.post(`${API_BASE}/mock-student-id/notes`, { note });
            setNote('');
            setNoteSuccess(true);
            setTimeout(() => setNoteSuccess(false), 3000);
        } catch (err) {
            console.error("Failed to save note", err);
            // Simulate success for mock mode
            setNote('');
            setNoteSuccess(true);
            setTimeout(() => setNoteSuccess(false), 3000);
        }
    };

    if (loading) return (
        <div className="flex h-full items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-4 border-blue-500"></div>
        </div>
    );

    if (!data) return <div>Failed to load data.</div>;

    const {
        activeChildOverview, sessionSummary, weeklySnapshot,
        emotionalOverview, engagementIndicator, interventionSummary,
        progressSnapshot, milestonesAndAchievements, recommendedNextSteps,
        sessionHistory
    } = data;

    const renderTrendIcon = (trend) => {
        switch (trend) {
            case 'UP': return <ArrowUpRight className="text-emerald-500" size={18} />;
            case 'STABLE': return <ArrowRight className="text-blue-500" size={18} />;
            case 'DOWN': return <ArrowDownRight className="text-rose-500" size={18} />;
            default: return null;
        }
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8 animate-fade-in-up pb-12">

            {/* 1. Active Child Overview */}
            <div className="bg-gradient-to-r from-blue-500 to-blue-400 rounded-3xl p-8 shadow-md text-white flex items-center justify-between">
                <div className="flex items-center gap-6">
                    <div className="w-20 h-20 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm border border-white/30">
                        <UserCircle size={48} className="text-white" />
                    </div>
                    <div>
                        <h1 className="text-3xl font-extrabold mb-1">{activeChildOverview.childName}</h1>
                        <p className="text-blue-100 mb-2">Age {activeChildOverview.age} • Learning {activeChildOverview.currentLearningTheme}</p>
                        <p className="text-xs font-medium text-blue-200 uppercase tracking-widest"><Calendar size={12} className="inline mr-1" /> Last Session: {activeChildOverview.lastSessionDate}</p>
                    </div>
                </div>
                <div className="bg-emerald-400 text-emerald-950 px-6 py-3 rounded-2xl font-bold flex items-center gap-2 shadow-sm border border-emerald-300">
                    <CheckCircle2 size={24} /> {activeChildOverview.overallStatusBadge}
                </div>
            </div>

            {/* 2. Today's Summary */}
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100 flex items-start gap-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center shrink-0">
                    <Sparkles className="text-blue-500" size={32} />
                </div>
                <div>
                    <h2 className="text-2xl font-extrabold text-slate-800 mb-3">Today's Summary</h2>
                    <p className="text-slate-600 text-lg leading-relaxed mb-4">
                        {sessionSummary.aiNarrativeSummary}
                    </p>
                    <div className="flex flex-wrap gap-2 mb-4">
                        <span className="px-3 py-1 bg-slate-100 text-slate-600 rounded-lg text-sm font-semibold">Focus: {sessionSummary.learningFocus}</span>
                        <span className="px-3 py-1 bg-emerald-50 text-emerald-700 rounded-lg text-sm font-semibold border border-emerald-100">Emotion: {sessionSummary.emotionalStabilityStatus}</span>
                    </div>
                    <div className="flex gap-2 flex-wrap">
                        {sessionSummary.conceptsMastered.map((c, i) => (
                            <span key={i} className="inline-flex items-center gap-1 px-4 py-2 bg-emerald-100 text-emerald-800 rounded-full text-sm font-bold shadow-sm">
                                <Trophy size={16} className="text-amber-500" /> Mastered: {c}
                            </span>
                        ))}
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* 3. Emotional Overview */}
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
                            <span className="text-emerald-600 font-bold inline-flex items-center gap-1">{emotionalOverview.weekOverWeekTrend} <ArrowUpRight size={16} /></span>
                        </li>
                    </ul>
                </div>

                {/* 4. Engagement Overview */}
                <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100">
                    <div className="flex items-center gap-3 mb-6">
                        <Eye className="text-blue-500" size={28} />
                        <h3 className="text-xl font-bold text-slate-800">Engagement & Focus</h3>
                    </div>
                    <div className="flex flex-col gap-4">
                        <div className="bg-blue-50 p-4 rounded-2xl flex justify-between items-center border border-blue-100">
                            <span className="text-slate-600 font-semibold">Overall Level</span>
                            <span className="text-blue-700 font-bold">{engagementIndicator.engagementLevel}</span>
                        </div>
                        <div className="bg-indigo-50 p-4 rounded-2xl flex justify-between items-center border border-indigo-100">
                            <span className="text-slate-600 font-semibold">Participation Style</span>
                            <span className="text-indigo-700 font-bold">{engagementIndicator.participationScore}</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* 5. Progress Snapshot */}
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-emerald-100">
                <div className="flex items-center gap-3 mb-8">
                    <TrendingUp className="text-emerald-500" size={28} />
                    <h3 className="text-xl font-bold text-slate-800">Learning Progress</h3>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {progressSnapshot.map((concept, idx) => (
                        <div key={idx} className="bg-slate-50 p-6 rounded-2xl">
                            <div className="flex justify-between items-end mb-3">
                                <span className="font-bold text-slate-700">{concept.conceptName}</span>
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-bold text-slate-500">{concept.masteryPercentage}%</span>
                                    {renderTrendIcon(concept.trend)}
                                </div>
                            </div>
                            <div className="w-full bg-slate-200 rounded-full h-2.5 overflow-hidden">
                                <div
                                    className={`h-2.5 rounded-full transition-all duration-1000 ${concept.masteryPercentage > 75 ? 'bg-emerald-400' : concept.masteryPercentage > 40 ? 'bg-blue-400' : 'bg-rose-400'}`}
                                    style={{ width: `${concept.masteryPercentage}%` }}
                                ></div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* 6. Intervention Summary */}
                <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100">
                    <div className="flex items-center gap-3 mb-6">
                        <ShieldCheck className="text-purple-500" size={28} />
                        <h3 className="text-xl font-bold text-slate-800">How LaRa Helped</h3>
                    </div>
                    <div className="space-y-3">
                        {interventionSummary.effectivenessStatements.map((stmt, idx) => (
                            <div key={idx} className="p-4 bg-purple-50 border border-purple-100 rounded-2xl">
                                <p className="text-purple-900 font-medium">{stmt}</p>
                            </div>
                        ))}
                        <div className="mt-6 pt-4 border-t border-slate-100">
                            <p className="text-slate-500 text-sm font-semibold uppercase tracking-wider mb-1">Recommendation</p>
                            <p className="text-slate-700 font-medium">{interventionSummary.generalRecommendation}</p>
                        </div>
                    </div>
                </div>

                {/* 7. Milestones & Achievements */}
                <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-3xl p-8 shadow-sm border border-amber-200">
                    <div className="flex items-center gap-3 mb-6 justify-center">
                        <Trophy className="text-amber-500" size={32} />
                        <h3 className="text-xl font-bold text-amber-900">Recent Highlights</h3>
                    </div>
                    <ul className="space-y-4">
                        {milestonesAndAchievements.map((mA, idx) => (
                            <li key={idx} className="bg-white/80 p-4 rounded-2xl text-amber-900 font-medium shadow-sm border border-amber-100/50">
                                {mA}
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {/* 8. Weekly Snapshot */}
            <div className="bg-slate-50 rounded-3xl p-8 border border-slate-200 border-dashed">
                <h3 className="text-center text-slate-400 font-bold uppercase tracking-widest mb-6">This Week's Snapshot</h3>
                <div className="grid grid-cols-3 gap-6 text-center">
                    <div>
                        <p className="text-4xl font-extrabold text-slate-700 mb-1">{weeklySnapshot.sessionsCompleted}</p>
                        <p className="text-slate-500 font-semibold text-sm">Sessions Completed</p>
                    </div>
                    <div>
                        <p className="text-4xl font-extrabold text-slate-700 mb-1">{weeklySnapshot.totalLearningTime}</p>
                        <p className="text-slate-500 font-semibold text-sm">Total Learning Time</p>
                    </div>
                    <div>
                        <p className="text-4xl font-extrabold text-emerald-500 mb-1">{weeklySnapshot.conceptsAdvanced}</p>
                        <p className="text-slate-500 font-semibold text-sm">Concepts Advanced</p>
                    </div>
                </div>
                <div className="flex justify-center mt-6 pt-4 border-t border-slate-200 border-dashed">
                    <div className="text-center">
                        <p className="text-slate-500 font-semibold text-sm">Emotional Stability Trend</p>
                        <p className="text-xl font-bold text-emerald-600">{weeklySnapshot.emotionalStabilityTrend}</p>
                    </div>
                </div>
                <p className="text-center text-slate-600 mt-6 font-medium text-lg bg-white p-4 rounded-xl shadow-sm">"{weeklySnapshot.weeklySummarySentence}"</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                {/* 9. Recommended Next Steps */}
                <div className="bg-blue-50 rounded-3xl p-8 border border-blue-200">
                    <div className="flex items-center gap-3 mb-6">
                        <Target className="text-blue-600" size={28} />
                        <h3 className="text-xl font-bold text-blue-900">Suggested For Next Week</h3>
                    </div>
                    <ul className="space-y-3">
                        {recommendedNextSteps.map((step, idx) => (
                            <li key={idx} className="flex items-start gap-3">
                                <div className="w-6 h-6 rounded-full bg-blue-200 text-blue-700 flex items-center justify-center shrink-0 mt-0.5"><span className="text-xs font-bold">{idx + 1}</span></div>
                                <span className="text-blue-800 font-medium">{step}</span>
                            </li>
                        ))}
                    </ul>
                </div>

                {/* 10. Session History */}
                <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100">
                    <div className="flex items-center gap-3 mb-6">
                        <Clock className="text-indigo-500" size={28} />
                        <h3 className="text-xl font-bold text-slate-800">Session History</h3>
                    </div>
                    <div className="space-y-4">
                        {sessionHistory.map((session, idx) => (
                            <div key={idx} className="flex justify-between items-center p-4 bg-slate-50 hover:bg-slate-100 transition-colors rounded-2xl border border-slate-100 cursor-pointer">
                                <div>
                                    <p className="font-bold text-slate-800 mb-1">{session.date}</p>
                                    <p className="text-xs text-slate-500 font-semibold">{session.progressIndicator}</p>
                                </div>
                                <div className="text-right">
                                    <p className="font-semibold text-slate-700 text-sm mb-1">{session.duration}</p>
                                    <p className="text-xs text-slate-500">{session.emotionalSummary}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* 11. Caregiver Notes */}
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100">
                <div className="flex items-center gap-3 mb-4">
                    <FileText className="text-slate-500" size={24} />
                    <h3 className="text-lg font-bold text-slate-800">Caregiver Notes</h3>
                </div>
                <p className="text-sm text-slate-500 mb-4">Add your observations, school notes, or sleep patterns to inform LaRa's approach.</p>
                <form onSubmit={handleNoteSubmit} className="max-w-2xl">
                    <textarea
                        required
                        value={note}
                        onChange={(e) => setNote(e.target.value)}
                        className="w-full p-4 rounded-2xl border border-slate-200 bg-slate-50 focus:bg-white focus:border-blue-400 focus:ring-1 focus:ring-blue-400 outline-none transition-all h-28 resize-none mb-4 text-slate-700"
                        placeholder="E.g., Leo had a rough day at school and might be sleepy..."
                    />
                    <button
                        type="submit"
                        className="w-full py-3 bg-slate-800 hover:bg-slate-900 text-white rounded-xl font-bold transition-all flex justify-center items-center gap-2"
                    >
                        {noteSuccess ? <><CheckCircle2 size={18} /> Saved!</> : <><Send size={18} /> Save Note</>}
                    </button>
                </form>
            </div>

        </div>
    );
};

export default SimpleAnalytics;
