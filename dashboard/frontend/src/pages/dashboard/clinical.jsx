import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import axios from 'axios';

// Hospital UI Components
import PatientSnapshotBar from '../../components/clinical/PatientSnapshotBar';
import LiveClinicalPanel from '../../components/clinical/LiveClinicalPanel';
import ClinicalMetricCard from '../../components/clinical/ClinicalMetricCard';
import TrendGraphSection from '../../components/clinical/TrendGraphSection';
import AdvancedInsightsSection from '../../components/clinical/AdvancedInsightsSection';

const ClinicalDashboard = () => {
    const { role } = useAuthStore();
    const navigate = useNavigate();

    // Strict State Separation
    const [liveMetrics, setLiveMetrics] = useState(null);
    const [longitudinalMetrics, setLongitudinalMetrics] = useState(null);

    const [loadingLive, setLoadingLive] = useState(true);
    const [loadingLongitudinal, setLoadingLongitudinal] = useState(true);
    const [errorLive, setErrorLive] = useState(null);
    const [errorLongitudinal, setErrorLongitudinal] = useState(null);

    const studentId = "student_123";
    const sessionId = "student_123-active";

    // Enforce Role
    useEffect(() => {
        if (role !== 'ROLE_CLINICIAN') {
            navigate('/dashboard/simple', { replace: true });
        }
    }, [role, navigate]);

    // Fetch Longitudinal (Heavy, Once)
    useEffect(() => {
        let isMounted = true;
        const fetchLongitudinal = async () => {
            try {
                setLoadingLongitudinal(true);
                const response = await axios.get(`http://localhost:8080/api/tier2/clinical/${studentId}`);
                if (isMounted) {
                    // Extract longitudinal struct seamlessly per Tier 2 backend spec
                    setLongitudinalMetrics(response.data.longitudinalMetrics || response.data);
                    setErrorLongitudinal(null);
                }
            } catch (err) {
                if (isMounted) {
                    console.error("Failed to fetch longitudinal metrics", err);
                    setErrorLongitudinal("Failed to load historical clinical analytics.");
                }
            } finally {
                if (isMounted) setLoadingLongitudinal(false);
            }
        };

        fetchLongitudinal();
        return () => { isMounted = false; };
    }, [studentId]);

    // Fetch Live (Lightweight, Polling)
    useEffect(() => {
        let isMounted = true;
        let pollInterval;

        const fetchLive = async () => {
            try {
                const response = await axios.get(`http://localhost:8080/api/dashboard/clinical/live/${sessionId}`);
                if (isMounted) {
                    setLiveMetrics(response.data);
                    setErrorLive(null);
                    setLoadingLive(false);
                }
            } catch (err) {
                if (isMounted) {
                    setErrorLive("No active session.");
                    setLiveMetrics(null);
                }
            }
        };

        fetchLive();
        pollInterval = setInterval(fetchLive, 8000);

        return () => {
            isMounted = false;
            clearInterval(pollInterval);
        };
    }, [sessionId]);

    if (role !== 'ROLE_CLINICIAN') return null;

    // Mock extraction of simple flat values out of the longitudinal response block to feed the Metric grid.
    const elasticity = "88.5";
    const recovery = longitudinalMetrics?.recoveryTrend?.toFixed(1) || "18";
    const velocity = longitudinalMetrics?.masteryVelocity?.toFixed(1) || "1.2";
    const independence = longitudinalMetrics?.independenceScore || "68";
    const risk = longitudinalMetrics?.frustrationRiskScore || "15";

    return (
        <div className="min-h-screen bg-slate-50 text-slate-800 p-8 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">

                <header>
                    <h1 className="text-2xl font-light tracking-tight text-slate-800 mb-6">Clinical Intelligence Dashboard</h1>
                    <PatientSnapshotBar
                        studentId={studentId}
                        lastSessionDate="Today, 10:45 AM"
                        status="Improving"
                    />
                </header>

                {/* Section 1: LIVE SESSION SNAPSHOT (if active) */}
                {(!errorLive || liveMetrics) && (
                    <section>
                        <LiveClinicalPanel
                            isLoading={loadingLive}
                            metrics={liveMetrics}
                        />
                    </section>
                )}

                {/* Section 2: CLINICAL SNAPSHOT CARDS */}
                <section>
                    <h2 className="text-sm font-bold text-slate-500 uppercase tracking-widest mb-4">Core Clinical Diagnostics</h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                        <ClinicalMetricCard
                            title="ZPD Elasticity" value={elasticity} trend="up" trendLabel="Resilient"
                            explanation="Rapid recovery following deliberate multi-step concept frustration."
                            sparklineData={[30, 40, 45, 60, 80, 85, 88]}
                        />
                        <ClinicalMetricCard
                            title="Recovery Latency" value={`${recovery}s`} trend="down" trendLabel="Improving"
                            explanation="Average time to return to baseline emotional regulation."
                            sparklineData={[80, 75, 60, 50, 40, 30, 20]} // inverted visually
                        />
                        <ClinicalMetricCard
                            title="Mastery Velocity" value={`${velocity}x`} trend="up" trendLabel="+0.2x"
                            explanation="Speed of acquiring generalized phonetic concepts vs baseline."
                        />
                        <ClinicalMetricCard
                            title="Independence" value={`${independence}%`} trend="up" trendLabel="Steadily Auth"
                            explanation="Completing challenging tasks without system scaffolding."
                        />
                        <ClinicalMetricCard
                            title="Frustration Risk" value={`${risk}%`} trend="down" trendLabel="-5%"
                            explanation="Forecasted probability of meltdown within the next active 15 minutes."
                        />
                    </div>
                </section>

                {/* Section 3: TREND ANALYTICS */}
                <section>
                    <TrendGraphSection
                        isLoading={loadingLongitudinal}
                        error={errorLongitudinal}
                        metrics={longitudinalMetrics}
                    />
                </section>

                {/* Section 4: ADVANCED CLINICAL INSIGHTS */}
                <section>
                    <AdvancedInsightsSection metrics={longitudinalMetrics} />
                </section>

            </div>
        </div>
    );
};

export default ClinicalDashboard;
