import { useState, useEffect } from 'react';
import AdminLayout from '../../components/dashboard/AdminLayout';
import api from '../../services/api';
import { 
    RadarChart, 
    Radar, 
    PolarGrid, 
    PolarAngleAxis, 
    ResponsiveContainer,
    LineChart,
    Line,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip
} from 'recharts';

export default function AdminModelEvaluation() {
    const [evaluation, setEvaluation] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchEval = async () => {
            try {
                const res = await api.get('/api/admin/model/evaluation');
                setEvaluation(res.data);
            } catch (err) {
                console.error('Model evaluation load failed', err);
            } finally {
                setLoading(false);
            }
        };
        fetchEval();
    }, []);

    if (loading) return <AdminLayout title="Evaluation" subtitle="Analyzing model accuracy..." />;

    const radarData = [
        { subject: 'Precision', A: (evaluation?.precision || 0) * 100, fullMark: 100 },
        { subject: 'Recall', A: (evaluation?.recall || 0) * 100, fullMark: 100 },
        { subject: 'F1 Score', A: (evaluation?.f1_score || 0) * 100, fullMark: 100 },
        { subject: 'ROC AUC', A: (evaluation?.roc_auc || 0) * 100, fullMark: 100 },
        { subject: 'Accuracy', A: (evaluation?.frustration_model_accuracy || 0) * 100, fullMark: 100 },
    ];

    return (
        <AdminLayout title="Model Evaluation" subtitle="Statistical performance analysis of LaRa's neural subsystems.">
            <div className="clinical-section-grid clinical-section-grid--two-column">
                <article className="clinical-panel">
                    <h3 className="clinical-panel__title">Model Performance Radar</h3>
                    <div style={{ width: '100%', height: '300px', marginTop: '24px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                                <PolarGrid stroke="#e2e8f0" />
                                <PolarAngleAxis dataKey="subject" tick={{ fontSize: 12, fill: '#64748b', fontWeight: 600 }} />
                                <Radar
                                    name="LaRa Core"
                                    dataKey="A"
                                    stroke="var(--color-primary)"
                                    fill="var(--color-primary)"
                                    fillOpacity={0.2}
                                />
                            </RadarChart>
                        </ResponsiveContainer>
                    </div>
                </article>

                <article className="clinical-panel">
                    <h3 className="clinical-panel__title">ROC Curve (Simulated)</h3>
                    <div style={{ width: '100%', height: '300px', marginTop: '24px' }}>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={evaluation?.roc_curve || []}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                                <XAxis dataKey="fpr" label={{ value: 'False Positive Rate', position: 'insideBottom', offset: -5, fontSize: 10 }} axisLine={false} tickLine={false} tick={{ fontSize: 10 }} />
                                <YAxis label={{ value: 'True Positive Rate', angle: -90, position: 'insideLeft', fontSize: 10 }} axisLine={false} tickLine={false} tick={{ fontSize: 10 }} />
                                <Tooltip />
                                <Line type="monotone" dataKey="tpr" stroke="var(--color-green)" strokeWidth={3} dot={false} />
                                <Line type="dashed" dataKey="fpr" stroke="#94a3b8" strokeDasharray="5 5" dot={false} />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </article>
            </div>
        </AdminLayout>
    );
}
