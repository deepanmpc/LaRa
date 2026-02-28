import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, ComposedChart
} from 'recharts';
import { ShieldAlert, TrendingDown, Activity, FastForward } from 'lucide-react';
import { ChartToolbar } from '../components/ChartToolbar';

const PredictivePanel = () => {
    // Mocking PredictiveRiskDto combined with Independence Index time-series
    const [data] = useState({
        frustrationRiskScore: 0.88,
        masteryStagnationProbability: 0.72,
        interventionEscalationLikelihood: 0.65,
        clinicalAlertTier: 3,
        alertRationale: "CRITICAL: Z-Score volatility exceeds normative bounds. Imminent escalation likely.",
        independenceTrajectory: [
            { session: 1, independenceScore: 80, overScaffoldingRisk: 20, errorMargin: [75, 85] },
            { session: 2, independenceScore: 78, overScaffoldingRisk: 25, errorMargin: [70, 86] },
            { session: 3, independenceScore: 75, overScaffoldingRisk: 30, errorMargin: [65, 85] },
            { session: 4, independenceScore: 70, overScaffoldingRisk: 45, errorMargin: [60, 80] },
            { session: 5, independenceScore: 65, overScaffoldingRisk: 55, errorMargin: [55, 75] },
            { session: 6, independenceScore: 68, overScaffoldingRisk: 50, errorMargin: [60, 76] },
            { session: 7, independenceScore: 60, overScaffoldingRisk: 70, errorMargin: [50, 70] },
        ]
    });

    const [zoomDomain, setZoomDomain] = useState([1, 7]);
    const [isPanning, setIsPanning] = useState(false);

    const handleZoomIn = () => setZoomDomain([zoomDomain[0] + 1, Math.max(zoomDomain[1] - 1, zoomDomain[0] + 2)]);
    const handleZoomOut = () => setZoomDomain([1, 7]); // Reset
    const handleExportCSV = () => console.log("Exporting CSV...");
    const handleExportPNG = () => console.log("Exporting PNG...");

    const getAlertColor = (tier) => {
        if (tier === 3) return "text-rose-500 bg-rose-500/10 border-rose-500/30";
        if (tier === 2) return "text-orange-500 bg-orange-500/10 border-orange-500/30";
        return "text-emerald-500 bg-emerald-500/10 border-emerald-500/30";
    };

    return (
        <div className="space-y-6">
            <header className="mb-8">
                <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2">
                    <FastForward className="text-primary-400" /> Early Risk & Predictive Engine
                </h1>
                <p className="text-slate-400 mt-1">Rolling 7-session anomaly forecasting and Independence mapping.</p>
            </header>

            {/* Top Level Clinical Alert Banner */}
            {data.clinicalAlertTier > 1 && (
                <div className={`p-4 rounded-xl border flex items-start gap-4 ${getAlertColor(data.clinicalAlertTier)}`}>
                    <ShieldAlert size={24} className="mt-1 shrink-0" />
                    <div>
                        <h3 className="font-bold text-sm uppercase tracking-wider mb-1">
                            Tier {data.clinicalAlertTier} Clinical Alert
                        </h3>
                        <p className="text-sm opacity-90">{data.alertRationale}</p>
                    </div>
                </div>
            )}

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Frustration Escalation Risk</h3>
                        <Activity size={18} className="text-rose-400" />
                    </div>
                    <span className="text-3xl font-bold text-white">{(data.frustrationRiskScore * 100).toFixed(0)}%</span>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Mastery Stagnation Prob.</h3>
                        <TrendingDown size={18} className="text-orange-400" />
                    </div>
                    <span className="text-3xl font-bold text-white">{(data.masteryStagnationProbability * 100).toFixed(0)}%</span>
                </div>

                <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-sm font-medium text-slate-400">Intervention Dependency</h3>
                        <ShieldAlert size={18} className="text-emerald-400" />
                    </div>
                    <span className="text-3xl font-bold text-white">{(data.interventionEscalationLikelihood * 100).toFixed(0)}%</span>
                </div>
            </div>

            {/* Independence Index 2.0 with Confidence Shading */}
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
                <ChartToolbar
                    title="Independence Score Trajectory (w/ Bayesian Intervals)"
                    onZoomIn={handleZoomIn}
                    onZoomOut={handleZoomOut}
                    onPanToggle={() => setIsPanning(!isPanning)}
                    isPanning={isPanning}
                    onExportCSV={handleExportCSV}
                    onExportPNG={handleExportPNG}
                />
                <div className="h-80 w-full" style={{ cursor: isPanning ? 'grab' : 'default' }}>
                    <ResponsiveContainer width="100%" height="100%">
                        <ComposedChart data={data.independenceTrajectory}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                            <XAxis dataKey="session" stroke="#94a3b8" fontSize={12} domain={zoomDomain} type="number" tickFormatter={(val) => `Session ${val}`} tickLine={false} axisLine={false} />
                            <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} domain={[0, 100]} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', borderRadius: '8px' }}
                                itemStyle={{ color: '#f1f5f9' }}
                            />
                            {/* Confidence Shading Area */}
                            <Area type="monotone" dataKey="errorMargin" fill="#6366f1" fillOpacity={0.15} stroke="none" name="95% Confidence" />
                            <Line type="monotone" dataKey="independenceScore" stroke="#818cf8" strokeWidth={3} dot={{ r: 4 }} name="Independence Score" />
                            <Line type="monotone" dataKey="overScaffoldingRisk" stroke="#ec4899" strokeWidth={2} strokeDasharray="5 5" name="Over-Scaffolding Risk" />
                        </ComposedChart>
                    </ResponsiveContainer>
                </div>
            </div>

        </div>
    );
};

export default PredictivePanel;
