import {
    Activity,
    AudioLines,
    BrainCircuit,
    Eye,
    ShieldCheck,
    Sparkles,
    History,
    TrendingUp,
    AlertTriangle,
    Network
} from 'lucide-react';
import { useState, useEffect, useRef, useCallback } from 'react';
import ForceGraph3D from 'react-force-graph-3d';
import SpriteText from 'three-spritetext';
import ChildDevelopmentTrajectory from './ChildDevelopmentTrajectory';

export function formatPercent(value) {
    if (value === null || value === undefined) return '0%';
    return `${Math.round(value * 100)}%`;
}

export function formatStyleLabel(style) {
    if (!style) return 'None';
    return style
        .split('_')
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' ');
}

function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
}

function polarToCartesian(cx, cy, radius, angleInDegrees) {
    const angleInRadians = (angleInDegrees * Math.PI) / 180;
    return {
        x: cx + (radius * Math.cos(angleInRadians)),
        y: cy + (radius * Math.sin(angleInRadians))
    };
}

function SectionBlock({ icon, label, title, subtitle, children }) {
    return (
        <section className="clinical-section">
            <div className="clinical-section__header">
                <div className="clinical-section__label-row">
                    <span className="clinical-section__icon">{icon}</span>
                    <span className="clinical-section__label">{label}</span>
                </div>
                <div>
                    <h2 className="clinical-section__title">{title}</h2>
                    <p className="clinical-section__subtitle">{subtitle}</p>
                </div>
            </div>
            {children}
        </section>
    );
}

function MetricTile({ label, value, tone = 'neutral' }) {
    return (
        <div className={`clinical-metric-tile clinical-metric-tile--${tone}`}>
            <span className="clinical-metric-tile__label">{label}</span>
            <span className="clinical-metric-tile__value">{value}</span>
        </div>
    );
}

function HorizontalBar({ label, value, percent, tone = 'blue' }) {
    return (
        <div className="clinical-progress-row">
            <div className="clinical-progress-row__meta">
                <span className="clinical-progress-row__label">{label}</span>
                <span className="clinical-progress-row__value">{value}</span>
            </div>
            <div className="clinical-progress-row__track">
                <div
                    className={`clinical-progress-row__fill clinical-progress-row__fill--${tone}`}
                    style={{ width: `${percent}%` }}
                />
            </div>
        </div>
    );
}

function RadialMasteryChart({ value }) {
    // Value is 0-5
    const normalized = clamp((value / 5) * 100, 0, 100);
    const radius = 58;
    const circumference = 2 * Math.PI * radius;
    const strokeOffset = circumference - ((normalized / 100) * circumference);

    return (
        <div className="clinical-radial">
            <svg viewBox="0 0 160 160" className="clinical-radial__svg" aria-hidden="true">
                <circle cx="80" cy="80" r={radius} className="clinical-radial__track" />
                <circle
                    cx="80"
                    cy="80"
                    r={radius}
                    className="clinical-radial__value-ring"
                    strokeDasharray={circumference}
                    strokeDashoffset={strokeOffset}
                    transform="rotate(-90 80 80)"
                />
            </svg>
            <div className="clinical-radial__content">
                <span className="clinical-radial__value">{value}</span>
                <span className="clinical-radial__unit">of 5</span>
            </div>
        </div>
    );
}

function EmotionStack({ data }) {
    // Expected emotion_distribution: [{emotion: 'Happy', count: 10}, ...]
    const total = data.reduce((acc, curr) => acc + curr.count, 0) || 1;
    
    const getTone = (emotion) => {
        const e = emotion.toLowerCase();
        if (e.includes('happy') || e.includes('calm') || e.includes('focus')) return 'positive';
        if (e.includes('frust') || e.includes('anx') || e.includes('sad')) return 'risk';
        return 'calm';
    };

    return (
        <div className="emotion-stack">
            <div className="emotion-stack__bar">
                {data.map((item) => (
                    <div
                        key={item.emotion}
                        className={`emotion-stack__segment emotion-stack__segment--${getTone(item.emotion)}`}
                        style={{ width: `${(item.count / total) * 100}%` }}
                    />
                ))}
            </div>

            <div className="emotion-stack__legend">
                {data.map((item) => (
                    <div key={item.emotion} className="emotion-stack__legend-item">
                        <span className={`emotion-stack__dot emotion-stack__dot--${getTone(item.emotion)}`} />
                        <span className="emotion-stack__legend-label">{item.emotion}</span>
                        <span className="emotion-stack__legend-value">{item.count}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}

function StabilityMeter({ value }) {
    return (
        <div className="stability-meter">
            <div className="stability-meter__header">
                <span className="stability-meter__label">Stability Index</span>
                <span className="stability-meter__value">{Math.round(value)}%</span>
            </div>
            <div className="stability-meter__track">
                <div className="stability-meter__fill" style={{ width: `${value}%` }} />
            </div>
            <div className="stability-meter__scale">
                <span>Escalation Risk</span>
                <span>Stable Regulation</span>
            </div>
        </div>
    );
}

function RadarChart({ metrics }) {
    const centerX = 130;
    const centerY = 130;
    const radius = 82;

    const levels = [0.25, 0.5, 0.75, 1].map((level) => (
        metrics.map((_, index) => {
            const angle = (-90 + ((360 / metrics.length) * index));
            const point = polarToCartesian(centerX, centerY, radius * level, angle);
            return `${point.x},${point.y}`;
        }).join(' ')
    ));

    const metricPoints = metrics.map((metric, index) => {
        const angle = (-90 + ((360 / metrics.length) * index));
        const point = polarToCartesian(centerX, centerY, radius * clamp(metric.value, 0, 1), angle);
        return `${point.x},${point.y}`;
    }).join(' ');

    return (
        <div className="clinical-radar">
            <svg viewBox="0 0 260 260" className="clinical-radar__svg" aria-hidden="true">
                {levels.map((points, index) => (
                    <polygon key={index} points={points} className={`clinical-radar__grid clinical-radar__grid--${index}`} />
                ))}

                {metrics.map((metric, index) => {
                    const angle = (-90 + ((360 / metrics.length) * index));
                    const outerPoint = polarToCartesian(centerX, centerY, radius, angle);
                    const labelPoint = polarToCartesian(centerX, centerY, radius + 24, angle);

                    return (
                        <g key={metric.label}>
                            <line
                                x1={centerX}
                                y1={centerY}
                                x2={outerPoint.x}
                                y2={outerPoint.y}
                                className="clinical-radar__axis"
                            />
                            <text
                                x={labelPoint.x}
                                y={labelPoint.y}
                                textAnchor="middle"
                                className="clinical-radar__label"
                            >
                                {metric.label}
                            </text>
                        </g>
                    );
                })}

                <polygon points={metricPoints} className="clinical-radar__area" />
                {metrics.map((metric, index) => {
                    const angle = (-90 + ((360 / metrics.length) * index));
                    const point = polarToCartesian(centerX, centerY, radius * clamp(metric.value, 0, 1), angle);

                    return <circle key={metric.label} cx={point.x} cy={point.y} r="4" className="clinical-radar__point" />;
                })}
            </svg>
        </div>
    );
}

function ProgressBar({ value, variant = 'primary' }) {
    return (
        <div className="progress-bar" style={{ height: 8, background: '#e2e8f0', borderRadius: 4, overflow: 'hidden' }}>
            <div 
                className={`progress-fill ${variant}`} 
                style={{ 
                    width: `${value}%`, 
                    height: '100%', 
                    background: variant === 'risk' ? '#ef4444' : variant === 'green' ? '#10b981' : '#3b82f6',
                    transition: 'width 0.5s ease'
                }} 
            />
        </div>
    );
}

export default function ClinicalStudentSections({ analytics, riskSignals, knowledgeGraph }) {
    if (!analytics) return null;

    const { cognitive, emotional, vision, reinforcement, longitudinal } = analytics;

    const radarMetrics = [
        { label: 'ENGAGE', value: vision?.radar?.ENGAGE || 0 },
        { label: 'GAZE', value: vision?.radar?.GAZE || 0 },
        { label: 'OBJECT', value: vision?.radar?.OBJECT || 0 },
        { label: 'GESTURE', value: vision?.radar?.GESTURE || 0 },
        { label: 'FACE', value: vision?.radar?.FACE || 0 },
        { label: 'SYSTEM', value: vision?.radar?.SYSTEM || 0 }
    ];

    const getNodeColor = (mastery) => {
        if (mastery < 0.3) return '#ef4444'; // Red
        if (mastery < 0.7) return '#f59e0b'; // Yellow
        return '#10b981'; // Green
    };

    return (
        <>
            {/* 0. Clinical Intelligence */}
            {riskSignals && (
                <SectionBlock
                    icon={<BrainCircuit size={18} strokeWidth={2.2} />}
                    label="Intelligence"
                    title="Clinical Intelligence Engine"
                    subtitle="Automated analysis of developmental risks and interaction effectiveness."
                >
                    <div className="clinical-section-grid clinical-section-grid--two-column">
                        <article className="clinical-panel">
                            <h3 className="clinical-panel__title">Behavioral Risk Signals</h3>
                            <div className="clinical-tiles-grid" style={{ marginTop: 16 }}>
                                <MetricTile 
                                    label="Frustration Risk" 
                                    value={riskSignals.frustrationRisk} 
                                    tone={riskSignals.frustrationRisk === 'HIGH' ? 'risk' : riskSignals.frustrationRisk === 'MEDIUM' ? 'amber' : 'green'} 
                                />
                                <MetricTile 
                                    label="Engagement Trend" 
                                    value={riskSignals.engagementTrend} 
                                    tone={riskSignals.engagementTrend === 'DECAYING' ? 'risk' : 'green'} 
                                />
                                <MetricTile 
                                    label="Mastery Velocity" 
                                    value={riskSignals.masteryVelocity} 
                                    tone={riskSignals.masteryVelocity === 'SLOW' ? 'amber' : 'green'} 
                                />
                                <MetricTile 
                                    label="ZPD Status" 
                                    value={riskSignals.zpdStatus?.replace('_', ' ')} 
                                    tone={riskSignals.zpdStatus?.startsWith('OPTIMAL') ? 'green' : 'amber'} 
                                />
                            </div>
                            
                            <div style={{ marginTop: 24 }}>
                                <h4 style={{ fontSize: 12, fontWeight: 700, color: 'var(--color-text-muted)', marginBottom: 12 }}>SYSTEM ALERTS</h4>
                                {riskSignals.alerts && riskSignals.alerts.length > 0 ? (
                                    riskSignals.alerts.map((alert, idx) => (
                                        <div key={idx} className={`alert-box alert-box--${alert.severity.toLowerCase()}`} style={{
                                            padding: '10px 14px',
                                            borderRadius: 8,
                                            marginBottom: 10,
                                            background: alert.severity === 'CRITICAL' ? '#fef2f2' : alert.severity === 'WARNING' ? '#fffbeb' : '#f0f9ff',
                                            border: `1px solid ${alert.severity === 'CRITICAL' ? '#fecaca' : alert.severity === 'WARNING' ? '#fde68a' : '#bae6fd'}`,
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 12
                                        }}>
                                            <AlertTriangle size={16} color={alert.severity === 'CRITICAL' ? '#ef4444' : alert.severity === 'WARNING' ? '#f59e0b' : '#3b82f6'} />
                                            <div>
                                                <div style={{ fontSize: 13, fontWeight: 700, color: '#1e293b' }}>{alert.alertType}</div>
                                                <div style={{ fontSize: 12, color: '#64748b' }}>{alert.message}</div>
                                            </div>
                                        </div>
                                    ))
                                ) : (
                                    <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>No active alerts for this period.</p>
                                )}
                            </div>
                        </article>

                        <article className="clinical-panel">
                            <h3 className="clinical-panel__title">Intervention Effectiveness</h3>
                            <p className="clinical-panel__subtitle">Success rate of specific therapeutic tools.</p>
                            <div style={{ marginTop: 16 }}>
                                {Object.entries(riskSignals.interventionEffectiveness || {}).map(([tool, rate]) => (
                                    <div key={tool} style={{ marginBottom: 16 }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                                            <span style={{ fontWeight: 600 }}>{tool}</span>
                                            <span>{Math.round(rate * 100)}% Success</span>
                                        </div>
                                        <ProgressBar value={rate * 100} variant={rate > 0.7 ? 'green' : rate > 0.4 ? 'primary' : 'risk'} />
                                    </div>
                                ))}
                                {Object.keys(riskSignals.interventionEffectiveness || {}).length === 0 && (
                                    <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>Insufficient intervention data.</p>
                                )}
                            </div>
                        </article>
                    </div>
                </SectionBlock>
            )}

            {/* 1. Child Overview */}
            <SectionBlock
                icon={<Activity size={18} strokeWidth={2.2} />}
                label="Overview"
                title="Clinical Snapshot"
                subtitle="High-level performance summary across all dimensions."
            >
                <div className="clinical-tiles-grid" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
                    <MetricTile label="Cognitive Mastery" value={`${Math.round(cognitive?.mastery_percentage || 0)}%`} tone="blue" />
                    <MetricTile label="Emotional Stability" value={`${Math.round(emotional?.regulation_index || 0)}%`} tone="green" />
                    <MetricTile label="Visual Engagement" value={formatPercent(vision?.avg_engagement)} tone="blue" />
                    <MetricTile label="Risk Indicator" value={longitudinal?.frustration_risk > 0.5 ? 'ELEVATED' : 'STABLE'} tone={longitudinal?.frustration_risk > 0.5 ? 'risk' : 'neutral'} />
                </div>
            </SectionBlock>

            {/* 2. Cognitive Development */}
            <SectionBlock
                icon={<BrainCircuit size={18} strokeWidth={2.2} />}
                label="Section 1"
                title="Cognitive Development"
                subtitle="Mastery tracking and concept acquisition metrics."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Mastery Gauge</h3>
                                <p className="clinical-panel__subtitle">Current concept: {cognitive?.active_concept}</p>
                            </div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 40, padding: '20px 0' }}>
                            <RadialMasteryChart value={cognitive?.mastery_level || 0} />
                            <div style={{ flex: 1 }}>
                                <HorizontalBar 
                                    label="Task Completion Reliability" 
                                    value={formatPercent(cognitive?.success_rate)} 
                                    percent={Math.round((cognitive?.success_rate || 0) * 100)} 
                                />
                                <div className="clinical-tiles-grid" style={{ marginTop: 20 }}>
                                    <MetricTile label="Total Attempts" value={cognitive?.attempt_count} />
                                    <MetricTile label="Active Concept" value={cognitive?.active_concept} tone="green" />
                                </div>
                            </div>
                        </div>
                    </article>
                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <h3 className="clinical-panel__title">Concept Distribution</h3>
                        </div>
                        <div style={{ padding: '10px 0' }}>
                            {cognitive?.distribution?.map(item => (
                                <div key={item.concept} style={{ marginBottom: 12 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                                        <span>{item.concept}</span>
                                        <span>{Math.round(item.mastery)}%</span>
                                    </div>
                                    <ProgressBar value={item.mastery} variant="primary" />
                                </div>
                            ))}
                        </div>
                    </article>
                </div>
            </SectionBlock>

            {/* 3. Emotional Regulation */}
            <SectionBlock
                icon={<ShieldCheck size={18} strokeWidth={2.2} />}
                label="Section 2"
                title="Emotional Regulation"
                subtitle="Mood trends and self-regulation efficiency."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <h3 className="clinical-panel__title">Emotion Distribution</h3>
                        </div>
                        <EmotionStack data={emotional?.emotion_distribution || []} />
                    </article>
                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <h3 className="clinical-panel__title">Regulation Index</h3>
                        </div>
                        <StabilityMeter value={emotional?.regulation_index || 50} />
                        <div className="clinical-tiles-grid" style={{ marginTop: 20 }}>
                            <MetricTile label="Frustration Freq" value={formatPercent(emotional?.frustration_frequency)} tone="risk" />
                            <MetricTile label="Baseline Stability" value={emotional?.baseline_stability?.toFixed(1)} tone="blue" />
                        </div>
                    </article>
                </div>
            </SectionBlock>

            {/* 4. Vision & Perception */}
            <SectionBlock
                icon={<Eye size={18} strokeWidth={2.2} />}
                label="Section 3"
                title="Vision & Perception"
                subtitle="Visual attention and multimodal confidence scores."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <RadarChart metrics={radarMetrics} />
                    </article>
                    <article className="clinical-panel">
                        <div className="clinical-tiles-grid">
                            <MetricTile label="Focus Duration" value={`${vision?.focus_duration?.toFixed(1)}m`} tone="green" />
                            <MetricTile label="Distraction Rate" value={vision?.distraction_rate} tone="risk" />
                            <MetricTile label="Avg Gaze Score" value={formatPercent(vision?.gaze_score)} tone="blue" />
                        </div>
                        <div style={{ marginTop: 24 }}>
                            <h4 style={{ fontSize: 12, fontWeight: 700, color: 'var(--color-text-muted)', marginBottom: 12 }}>PERCEPTION CONFIDENCE</h4>
                            <HorizontalBar label="Face" value={formatPercent(vision?.radar?.FACE)} percent={(vision?.radar?.FACE || 0) * 100} tone="green" />
                            <HorizontalBar label="Gesture" value={formatPercent(vision?.radar?.GESTURE)} percent={(vision?.radar?.GESTURE || 0) * 100} tone="blue" />
                            <HorizontalBar label="Object" value={formatPercent(vision?.radar?.OBJECT)} percent={(vision?.radar?.OBJECT || 0) * 100} tone="amber" />
                        </div>
                    </article>
                </div>
            </SectionBlock>

            {/* 5. Reinforcement Intelligence */}
            <SectionBlock
                icon={<Sparkles size={18} strokeWidth={2.2} />}
                label="Section 4"
                title="Reinforcement Intelligence"
                subtitle="Effectiveness of different adaptive interaction styles."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <h3 className="clinical-panel__title">Strategy Effectiveness</h3>
                        <div style={{ padding: '20px 0' }}>
                            {reinforcement?.effectiveness?.map(eff => (
                                <div key={eff.strategy} style={{ marginBottom: 16 }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13, marginBottom: 6 }}>
                                        <span style={{ fontWeight: 600 }}>{formatStyleLabel(eff.strategy)}</span>
                                        <span>{formatPercent(eff.rate)} Success</span>
                                    </div>
                                    <ProgressBar value={(eff.rate || 0) * 100} variant={eff.strategy === reinforcement?.primary_strategy ? 'green' : 'primary'} />
                                </div>
                            ))}
                        </div>
                    </article>
                    <article className="clinical-panel">
                        <div className="reinforcement-summary__hero">
                            <span className="reinforcement-summary__label">Optimal Strategy</span>
                            <span className="reinforcement-summary__value" style={{ fontSize: 24 }}>{formatStyleLabel(reinforcement?.primary_strategy)}</span>
                            <div className="clinical-tiles-grid" style={{ marginTop: 20 }}>
                                <MetricTile label="Total Events" value={reinforcement?.total_events} />
                                <MetricTile label="Avg Success" value={formatPercent(reinforcement?.success_rate)} tone="green" />
                            </div>
                        </div>
                    </article>
                </div>
            </SectionBlock>

            {/* 6. Session History */}
            <SectionBlock
                icon={<History size={18} strokeWidth={2.2} />}
                label="Section 5"
                title="Session History"
                subtitle="Historical log of recent clinical interactions."
            >
                <article className="clinical-panel clinical-panel--wide">
                    <div className="session-table-container" style={{ overflowX: 'auto' }}>
                        <table className="session-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ textAlign: 'left', borderBottom: '1px solid #e2e8f0', color: 'var(--color-text-muted)', fontSize: 12 }}>
                                    <th style={{ padding: '12px 8px' }}>DATE</th>
                                    <th style={{ padding: '12px 8px' }}>DURATION</th>
                                    <th style={{ padding: '12px 8px' }}>ENGAGEMENT</th>
                                    <th style={{ padding: '12px 8px' }}>MOOD</th>
                                    <th style={{ padding: '12px 8px' }}>DIFFICULTY</th>
                                    <th style={{ padding: '12px 8px' }}>TURNS</th>
                                </tr>
                            </thead>
                            <tbody>
                                {analytics.sessionHistory?.map(s => (
                                    <tr key={s.id} style={{ borderBottom: '1px solid #f1f5f9', fontSize: 13 }}>
                                        <td style={{ padding: '12px 8px', fontWeight: 600 }}>{new Date(s.date).toLocaleDateString()}</td>
                                        <td style={{ padding: '12px 8px' }}>{Math.round(s.duration / 60)} min</td>
                                        <td style={{ padding: '12px 8px' }}>{Math.round((s.engagement || 0) * 100)}%</td>
                                        <td style={{ padding: '12px 8px' }}><span className={`mood-tag mood-tag--${s.mood}`}>{s.mood}</span></td>
                                        <td style={{ padding: '12px 8px' }}>Lvl {s.difficulty}</td>
                                        <td style={{ padding: '12px 8px' }}>{s.turns || 0}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </article>
            </SectionBlock>

            {/* 7. Longitudinal Development */}
            <SectionBlock
                icon={<TrendingUp size={18} strokeWidth={2.2} />}
                label="Section 6"
                title="Longitudinal Development"
                subtitle="Cross-session trends and risk assessments."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel">
                        <h3 className="clinical-panel__title">Mastery Velocity</h3>
                        <div style={{ padding: '20px 0' }}>
                            <div style={{ fontSize: 32, fontWeight: 800, color: 'var(--color-primary)' }}>
                                {longitudinal?.mastery_velocity?.toFixed(2)}
                                <span style={{ fontSize: 14, fontWeight: 600, marginLeft: 8, color: 'var(--color-text-muted)' }}>% / session</span>
                            </div>
                            <p style={{ fontSize: 12, marginTop: 8, color: 'var(--color-text-muted)' }}>Rate of concept acquisition over time.</p>
                        </div>
                    </article>
                    <article className="clinical-panel">
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
                            <AlertTriangle size={20} color={longitudinal?.frustration_risk > 0.5 ? '#ef4444' : '#10b981'} />
                            <h3 className="clinical-panel__title">Risk Indicators</h3>
                        </div>
                        <div className="risk-stack">
                            <div style={{ marginBottom: 12 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                                    <span>Frustration Risk</span>
                                    <span>{Math.round((longitudinal?.frustration_risk || 0) * 100)}%</span>
                                </div>
                                <ProgressBar value={(longitudinal?.frustration_risk || 0) * 100} variant={longitudinal?.frustration_risk > 0.5 ? 'risk' : 'green'} />
                            </div>
                            <div style={{ marginBottom: 12 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                                    <span>Engagement Volatility</span>
                                    <span>{Math.round((longitudinal?.engagement_volatility || 0) * 100)}%</span>
                                </div>
                                <ProgressBar value={(longitudinal?.engagement_volatility || 0) * 100} variant="primary" />
                            </div>
                        </div>
                    </article>
                </div>
            </SectionBlock>

            <ChildDevelopmentTrajectory childId={analytics?.patient?.id} />

            {/* 8. Learning Concept Graph (Step 6) */}
            {knowledgeGraph && (
                <SectionBlock
                    icon={<Network size={18} strokeWidth={2.2} />}
                    label="Knowledge"
                    title="Learning Concept Graph"
                    subtitle="Interactive mapping of concept dependencies and mastery progress."
                >
                    <div className="clinical-section-grid clinical-section-grid--two-column">
                        <article className="clinical-panel clinical-panel--wide" style={{ height: '500px', padding: 0, overflow: 'hidden', position: 'relative', background: '#000', borderRadius: '12px' }}>
                            <ForceGraph3D
                                graphData={{
                                    nodes: knowledgeGraph.nodes.map(n => ({ ...n, color: n.isBlocked ? '#64748b' : getNodeColor(n.mastery) })),
                                    links: knowledgeGraph.edges
                                }}
                                nodeLabel={node => `${node.label}: ${Math.round(node.mastery * 100)}% ${node.isBlocked ? '(BLOCKED)' : ''}`}
                                nodeColor={node => node.color}
                                nodeThreeObject={node => {
                                    const sprite = new SpriteText(node.label);
                                    sprite.color = node.color;
                                    sprite.textHeight = 8;
                                    return sprite;
                                }}
                                linkDirectionalArrowLength={3.5}
                                linkDirectionalArrowRelPos={1}
                                linkCurvature={0.25}
                                backgroundColor="#000"
                                width={800}
                                height={500}
                            />
                        </article>
                        <article className="clinical-panel">
                            <h3 className="clinical-panel__title">Graph Insights</h3>
                            <div style={{ marginTop: 16 }}>
                                {knowledgeGraph.insights && knowledgeGraph.insights.length > 0 ? (
                                    knowledgeGraph.insights.map((insight, idx) => (
                                        <div key={idx} style={{ 
                                            padding: '12px', 
                                            borderRadius: 8, 
                                            background: '#f8fafc', 
                                            border: '1px solid #e2e8f0',
                                            marginBottom: 10,
                                            fontSize: 13,
                                            display: 'flex',
                                            alignItems: 'center',
                                            gap: 10
                                        }}>
                                            <Sparkles size={16} color="#3b82f6" />
                                            {insight}
                                        </div>
                                    ))
                                ) : (
                                    <p style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>No specific bottlenecks detected.</p>
                                )}
                            </div>
                            <div style={{ marginTop: 24 }}>
                                <h4 style={{ fontSize: 12, fontWeight: 700, color: 'var(--color-text-muted)', marginBottom: 12 }}>LEGEND</h4>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 8, fontSize: 12 }}>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <div style={{ width: 12, height: 12, borderRadius: 6, background: '#10b981' }}></div>
                                        <span>Mastered (&gt;70%)</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <div style={{ width: 12, height: 12, borderRadius: 6, background: '#f59e0b' }}></div>
                                        <span>In Progress (30-70%)</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <div style={{ width: 12, height: 12, borderRadius: 6, background: '#ef4444' }}></div>
                                        <span>Beginning (&lt;30%)</span>
                                    </div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                                        <div style={{ width: 12, height: 12, borderRadius: 6, background: '#64748b' }}></div>
                                        <span>Blocked by Prerequisite</span>
                                    </div>
                                </div>
                            </div>
                        </article>
                    </div>
                </SectionBlock>
            )}
        </>
    );
}
