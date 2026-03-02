import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';
import LiveClinicalPanel from '../../components/clinical/LiveClinicalPanel';
import LongitudinalAnalyticsPanel from '../../components/clinical/LongitudinalAnalyticsPanel';
import AdvancedClinicalPanel from '../../components/clinical/AdvancedClinicalPanel';
import { AlertCircle } from 'lucide-react';
import axios from 'axios';

const ClinicalDashboard = () => {
    // 1. Role Protection
    const { role } = useAuthStore();
    const navigate = useNavigate();

    // 2. Strict State Separation (Live vs Longitudinal)
    const [liveMetrics, setLiveMetrics] = useState(null);
    const [longitudinalMetrics, setLongitudinalMetrics] = useState(null);

    const [loadingLive, setLoadingLive] = useState(true);
    const [loadingLongitudinal, setLoadingLongitudinal] = useState(true);

    const [errorLive, setErrorLive] = useState(null);
    const [errorLongitudinal, setErrorLongitudinal] = useState(null);

    const studentId = "student_123"; // Mock active student ID; ideally passed via path or global state
    const sessionId = "student_123-active"; // Mock active session

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
                // Based on our Hybrid Spec, the API endpoint is /api/tier2/clinical/{studentId}
                const response = await axios.get(`http://localhost:8080/api/tier2/clinical/${studentId}`);
                if (isMounted) {
                    setLongitudinalMetrics(response.data);
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
                // Spec calls for sub-100ms lightweight fetch on /live endpoint
                const response = await axios.get(`http://localhost:8080/api/dashboard/clinical/live/${sessionId}`);
                if (isMounted) {
                    setLiveMetrics(response.data);
                    setErrorLive(null);
                    setLoadingLive(false); // Only set loading true on initial mount
                }
            } catch (err) {
                if (isMounted) {
                    console.warn("Live metrics unavailable:", err);
                    setErrorLive("Live session metrics temporarily unavailable.");
                    setLiveMetrics(null);
                }
            }
        };

        // Initial fetch
        fetchLive();

        // Specific requirement: 5-10s polling interval
        pollInterval = setInterval(fetchLive, 8000);

        return () => {
            isMounted = false;
            clearInterval(pollInterval);
        };
    }, [sessionId]);

    if (role !== 'ROLE_CLINICIAN') return null; // Wait for redirect

    return (
        <div className="min-h-screen bg-slate-50 text-slate-900 p-8 font-sans">
            <div className="max-w-7xl mx-auto space-y-8">

                {/* Header Section */}
                <header className="flex justify-between items-end border-b border-slate-200 pb-4">
                    <div>
                        <h1 className="text-3xl font-light tracking-tight text-slate-800">
                            Hybrid Clinical Dashboard
                        </h1>
                        <p className="text-sm text-slate-500 mt-1 uppercase tracking-wide">
                            Tier 2 Analytics • {studentId}
                        </p>
                    </div>
                </header>

                {/* Layer 1: Live Session Panel (Top Layer) */}
                <section>
                    {errorLive && !liveMetrics ? (
                        <div className="bg-amber-50 border-l-4 border-amber-400 p-4 rounded-md flex items-center gap-3">
                            <AlertCircle className="text-amber-500" size={20} />
                            <p className="text-sm text-amber-800">No active session detected. Live metrics hidden.</p>
                        </div>
                    ) : (
                        <LiveClinicalPanel
                            isLoading={loadingLive}
                            metrics={liveMetrics}
                        />
                    )}
                </section>

                {/* Layer 2: Longitudinal Analytics Panel (Middle Layer) */}
                <section>
                    <LongitudinalAnalyticsPanel
                        isLoading={loadingLongitudinal}
                        error={errorLongitudinal}
                        metrics={longitudinalMetrics?.longitudinalMetrics || longitudinalMetrics} // handle nested struct
                    />
                </section>

                {/* Layer 3: Advanced Clinical Insights (Bottom Layer) */}
                <section>
                    <AdvancedClinicalPanel
                        metrics={longitudinalMetrics?.longitudinalMetrics || longitudinalMetrics}
                    />
                </section>

            </div>
        </div>
    );
};

export default ClinicalDashboard;
