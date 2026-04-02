import {
    Activity,
    AudioLines,
    BrainCircuit,
    Eye,
    ShieldCheck,
    Sparkles,
    Tags
} from 'lucide-react';
import {
    formatPercent,
    formatStyleLabel,
    getReinforcementRanking,
    getStabilityIndex
} from '../../data/clinicalStudentMock';

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
    const total = data.frustration_count + data.recovery_count + data.neutral_stability_count;
    const items = [
        {
            label: 'Frustration Frequency',
            value: data.frustration_count,
            tone: 'risk'
        },
        {
            label: 'Recovery Efficiency',
            value: data.recovery_count,
            tone: 'positive'
        },
        {
            label: 'Baseline Stability',
            value: data.neutral_stability_count,
            tone: 'calm'
        }
    ];

    return (
        <div className="emotion-stack">
            <div className="emotion-stack__bar">
                {items.map((item) => (
                    <div
                        key={item.label}
                        className={`emotion-stack__segment emotion-stack__segment--${item.tone}`}
                        style={{ width: `${(item.value / total) * 100}%` }}
                    />
                ))}
            </div>

            <div className="emotion-stack__legend">
                {items.map((item) => (
                    <div key={item.label} className="emotion-stack__legend-item">
                        <span className={`emotion-stack__dot emotion-stack__dot--${item.tone}`} />
                        <span className="emotion-stack__legend-label">{item.label}</span>
                        <span className="emotion-stack__legend-value">{item.value}</span>
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
                <span className="stability-meter__value">{value}%</span>
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
        const point = polarToCartesian(centerX, centerY, radius * metric.value, angle);
        return `${point.x},${point.y}`;
    }).join(' ');

    return (
        <div className="clinical-radar">
            <svg viewBox="0 0 260 260" className="clinical-radar__svg" aria-hidden="true">
                {levels.map((points, index) => (
                    <polygon key={points} points={points} className={`clinical-radar__grid clinical-radar__grid--${index}`} />
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
                    const point = polarToCartesian(centerX, centerY, radius * metric.value, angle);

                    return <circle key={metric.label} cx={point.x} cy={point.y} r="4" className="clinical-radar__point" />;
                })}
            </svg>
        </div>
    );
}

function AttentionTimeline({ focusedDuration, sessionDuration, distractionFrames }) {
    const distractionSlots = Math.max(1, Math.min(4, Math.round(distractionFrames / 6)));
    const distractionIndices = [2, 6, 9, 11].slice(0, distractionSlots);
    const segmentCount = 12;
    const focusRatio = clamp(focusedDuration / sessionDuration, 0, 1);
    const minimumFocused = Math.max(1, Math.round(segmentCount * focusRatio));
    const segments = Array.from({ length: segmentCount }, (_, index) => {
        if (distractionIndices.includes(index)) {
            return 'risk';
        }

        return index < minimumFocused ? 'focused' : 'neutral';
    });

    return (
        <div className="attention-timeline">
            <div className="attention-timeline__segments">
                {segments.map((segment, index) => (
                    <span key={`${segment}-${index}`} className={`attention-timeline__segment attention-timeline__segment--${segment}`} />
                ))}
            </div>
            <div className="attention-timeline__meta">
                <span>Focus Retention {focusedDuration} min</span>
                <span>{distractionFrames} distraction frames</span>
            </div>
        </div>
    );
}

function VoiceLineChart({ speakingRate, volume, stabilityScore }) {
    const values = [
        { label: 'Speaking Rate', value: clamp(speakingRate / 140, 0, 1) },
        { label: 'Volume', value: clamp(volume, 0, 1) },
        { label: 'Speech Stability', value: clamp(stabilityScore, 0, 1) }
    ];
    const width = 320;
    const height = 150;
    const points = values.map((item, index) => {
        const x = 24 + ((width - 48) / (values.length - 1)) * index;
        const y = 18 + ((height - 36) * (1 - item.value));
        return `${x},${y}`;
    }).join(' ');

    return (
        <div className="voice-line-chart">
            <svg viewBox={`0 0 ${width} ${height}`} className="voice-line-chart__svg" aria-hidden="true">
                <line x1="24" y1="132" x2="296" y2="132" className="voice-line-chart__axis" />
                <polyline points={points} className="voice-line-chart__line" />
                {values.map((item, index) => {
                    const x = 24 + ((width - 48) / (values.length - 1)) * index;
                    const y = 18 + ((height - 36) * (1 - item.value));

                    return (
                        <g key={item.label}>
                            <circle cx={x} cy={y} r="5" className="voice-line-chart__point" />
                            <text x={x} y="146" textAnchor="middle" className="voice-line-chart__label">
                                {item.label}
                            </text>
                        </g>
                    );
                })}
            </svg>
        </div>
    );
}

function EngagementGauge({ value }) {
    const normalized = clamp(value, 0, 100);
    const startAngle = 180;
    const endAngle = 360;
    const radius = 74;
    const cx = 100;
    const cy = 115;
    const startPoint = polarToCartesian(cx, cy, radius, startAngle);
    const endPoint = polarToCartesian(cx, cy, radius, endAngle);
    const gaugePath = `M ${startPoint.x} ${startPoint.y} A ${radius} ${radius} 0 0 1 ${endPoint.x} ${endPoint.y}`;
    const angle = 180 + ((normalized / 100) * 180);
    const needlePoint = polarToCartesian(cx, cy, 60, angle);
    const valuePoint = polarToCartesian(cx, cy, radius + 20, angle);

    return (
        <div className="engagement-gauge">
            <svg viewBox="0 0 200 170" className="engagement-gauge__svg" aria-hidden="true">
                <path className="engagement-gauge__track" d={gaugePath} pathLength="100" />
                <path
                    className="engagement-gauge__fill"
                    d={gaugePath}
                    pathLength="100"
                    strokeDasharray={`${normalized} 100`}
                />
                <line
                    className="engagement-gauge__needle"
                    x1={cx}
                    y1={cy}
                    x2={needlePoint.x}
                    y2={needlePoint.y}
                />
                <circle cx={cx} cy={cy} r="8" className="engagement-gauge__hub" />
                <text 
                    x={valuePoint.x} 
                    y={valuePoint.y} 
                    textAnchor="middle" 
                    className="engagement-gauge__value"
                    style={{ fontSize: '20px' }}
                >
                    {normalized}%
                </text>
                <text x={cx} y={cy + 38} textAnchor="middle" className="engagement-gauge__label">
                    Overall Engagement Index
                </text>
            </svg>
        </div>
    );
}

export default function ClinicalStudentSections({ record }) {
    const stabilityIndex = getStabilityIndex(record.emotional_metrics);
    const reinforcementRanking = getReinforcementRanking(record.reinforcement_metrics);
    const bestStrategy = reinforcementRanking[0];
    const emotionalTrendChips = [
        record.emotional_metrics.frustration_count <= 8 ? 'Frustration within monitored range' : 'Escalation threshold elevated',
        record.emotional_metrics.recovery_count >= record.emotional_metrics.frustration_count ? 'Recovery exceeds disruption events' : 'Recovery below target response',
        record.emotional_metrics.neutral_stability_count >= 20 ? 'Baseline stability sustained' : 'Baseline variability noted'
    ];
    const radarMetrics = [
        { label: 'Engage', value: record.vision_session_stats.avg_engagement_score },
        { label: 'Gaze', value: record.vision_session_stats.avg_gaze_score },
        { label: 'System', value: record.vision_session_stats.system_confidence },
        { label: 'Face', value: record.perception_confidence.face_conf },
        { label: 'Gesture', value: record.perception_confidence.gesture_conf },
        { label: 'Object', value: record.perception_confidence.object_conf }
    ];
    const vocalDistribution = [
        { label: 'Neutral', value: record.vocal_mood_distribution.neutral, tone: 'calm' },
        { label: 'Arousal', value: record.vocal_mood_distribution.arousal, tone: 'alert' },
        { label: 'Withdrawal', value: record.vocal_mood_distribution.withdrawal, tone: 'risk' }
    ];

    return (
        <>
            <SectionBlock
                icon={<BrainCircuit size={18} strokeWidth={2.2} />}
                label="Section 1"
                title="Cognitive Development"
                subtitle="Concept acquisition, task reliability, and intervention readiness for the current learning target."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Cognitive Mastery</h3>
                                <p className="clinical-panel__subtitle">Current acquisition profile for {record.learning_progress.concept_name}</p>
                            </div>
                        </div>

                        <div className="cognitive-panel">
                            <div className="cognitive-panel__chart-container">
                                <RadialMasteryChart value={record.learning_progress.mastery_level} />
                                <span className="cognitive-panel__chart-label">Cognitive Mastery</span>
                            </div>

                            <div className="cognitive-panel__details">
                                <HorizontalBar
                                    label="Task Completion Reliability"
                                    value={formatPercent(record.learning_progress.success_rate)}
                                    percent={Math.round(record.learning_progress.success_rate * 100)}
                                    tone="blue"
                                />
                                <div className="clinical-tiles-grid">
                                    <MetricTile label="Learning Attempts" value={record.learning_progress.attempt_count} />
                                    <MetricTile label="Current Target" value={record.learning_progress.concept_name} tone="green" />
                                </div>
                            </div>
                        </div>
                    </article>

                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Learning Preferences</h3>
                                <p className="clinical-panel__subtitle">Profile modifiers from user preferences and instruction structure.</p>
                            </div>
                            <span className="clinical-panel__badge">
                                <Tags size={14} strokeWidth={2.2} />
                                Profile modifiers
                            </span>
                        </div>

                        <div className="profile-panel">
                            <div className="profile-panel__group">
                                <span className="profile-panel__label">Preferred Topics</span>
                                <div className="profile-panel__chips">
                                    {record.user_profiles.preferred_topics.map((topic) => (
                                        <span key={topic} className="profile-panel__chip">
                                            {topic}
                                        </span>
                                    ))}
                                </div>
                            </div>

                            <div className="profile-panel__group">
                                <span className="profile-panel__label">Instruction Complexity Level</span>
                                <div className="profile-panel__complexity-card">
                                    <span className="profile-panel__complexity-value">Level {record.user_profiles.instruction_depth}</span>
                                    <span className="profile-panel__complexity-caption">Moderate verbal scaffolding required</span>
                                </div>
                            </div>
                        </div>
                    </article>
                </div>
            </SectionBlock>

            <SectionBlock
                icon={<ShieldCheck size={18} strokeWidth={2.2} />}
                label="Section 2"
                title="Emotional & Behavioral Stability"
                subtitle="Observed regulation state, recovery response, and baseline emotional stability across recent sessions."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Emotional Regulation</h3>
                                <p className="clinical-panel__subtitle">Relative distribution of frustration, recovery, and stable baseline periods.</p>
                            </div>
                        </div>

                        <EmotionStack data={record.emotional_metrics} />

                        <div className="clinical-trend-chips">
                            {emotionalTrendChips.map((chip) => (
                                <span key={chip} className="clinical-trend-chip">
                                    {chip}
                                </span>
                            ))}
                        </div>
                    </article>

                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Regulation Index</h3>
                                <p className="clinical-panel__subtitle">Composite stability calculation using regulation and baseline counts.</p>
                            </div>
                        </div>

                        <StabilityMeter value={stabilityIndex} />

                        <div className="clinical-tiles-grid">
                            <MetricTile label="Frustration Frequency" value={record.emotional_metrics.frustration_count} tone="risk" />
                            <MetricTile label="Recovery Efficiency" value={record.emotional_metrics.recovery_count} tone="green" />
                            <MetricTile label="Baseline Stability" value={record.emotional_metrics.neutral_stability_count} tone="blue" />
                        </div>
                    </article>
                </div>
            </SectionBlock>

            <SectionBlock
                icon={<Eye size={18} strokeWidth={2.2} />}
                label="Section 3"
                title="Sensory & Perception Analysis"
                subtitle="Visual attention, multimodal confidence, and attention retention across the observed session window."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Visual Attention & Sensor Confidence</h3>
                                <p className="clinical-panel__subtitle">Radar summary across engagement, gaze, system confidence, and perception channels.</p>
                            </div>
                        </div>

                        <RadarChart metrics={radarMetrics} />
                    </article>

                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Behavioral Signals</h3>
                                <p className="clinical-panel__subtitle">Perception confidence and focus retention markers used during review.</p>
                            </div>
                        </div>

                        <div className="confidence-stack">
                            <HorizontalBar label="Face Confidence" value={formatPercent(record.perception_confidence.face_conf)} percent={Math.round(record.perception_confidence.face_conf * 100)} tone="green" />
                            <HorizontalBar label="Gesture Confidence" value={formatPercent(record.perception_confidence.gesture_conf)} percent={Math.round(record.perception_confidence.gesture_conf * 100)} tone="blue" />
                            <HorizontalBar label="Object Confidence" value={formatPercent(record.perception_confidence.object_conf)} percent={Math.round(record.perception_confidence.object_conf * 100)} tone="blue" />
                        </div>

                        <AttentionTimeline
                            focusedDuration={record.vision_behavior_counts.focused_duration}
                            sessionDuration={record.total_engagement_summary.session_duration}
                            distractionFrames={record.vision_behavior_counts.distraction_frames}
                        />

                        <div className="clinical-tiles-grid">
                            <MetricTile label="Engagement Signal" value={formatPercent(record.vision_session_stats.avg_engagement_score)} tone="blue" />
                            <MetricTile label="Visual Attention" value={formatPercent(record.vision_session_stats.avg_gaze_score)} tone="blue" />
                            <MetricTile label="Focus Retention" value={`${record.vision_behavior_counts.focused_duration} min`} tone="green" />
                            <MetricTile label="Sensor Confidence" value={formatPercent(record.vision_session_stats.system_confidence)} />
                        </div>
                    </article>
                </div>
            </SectionBlock>

            <SectionBlock
                icon={<AudioLines size={18} strokeWidth={2.2} />}
                label="Section 4"
                title="Voice & Communication Patterns"
                subtitle="Speech stability, vocal engagement, and emotional tone distribution from the current communication profile."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Speech Stability</h3>
                                <p className="clinical-panel__subtitle">Relative prosody profile across speaking rate, vocal amplitude, and stability score.</p>
                            </div>
                        </div>

                        <VoiceLineChart
                            speakingRate={record.voice_prosody_metrics.speaking_rate}
                            volume={record.voice_prosody_metrics.volume}
                            stabilityScore={record.voice_prosody_metrics.stability_score}
                        />

                        <div className="clinical-tiles-grid">
                            <MetricTile label="Speaking Rate" value={`${record.voice_prosody_metrics.speaking_rate} wpm`} />
                            <MetricTile label="Vocal Engagement" value={formatPercent(record.voice_prosody_metrics.volume)} tone="blue" />
                            <MetricTile label="Communication Consistency" value={formatPercent(record.voice_prosody_metrics.stability_score)} tone="green" />
                        </div>
                    </article>

                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Emotional Vocal Tone</h3>
                                <p className="clinical-panel__subtitle">Distribution of neutral, arousal, and withdrawal states detected in vocal output.</p>
                            </div>
                        </div>

                        <div className="vocal-distribution">
                            {vocalDistribution.map((entry) => (
                                <div key={entry.label} className="vocal-distribution__row">
                                    <div className="vocal-distribution__meta">
                                        <span className="vocal-distribution__label">{entry.label}</span>
                                        <span className="vocal-distribution__value">{formatPercent(entry.value)}</span>
                                    </div>
                                    <div className="vocal-distribution__track">
                                        <div
                                            className={`vocal-distribution__fill vocal-distribution__fill--${entry.tone}`}
                                            style={{ width: `${Math.round(entry.value * 100)}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </article>
                </div>
            </SectionBlock>

            <SectionBlock
                icon={<Activity size={18} strokeWidth={2.2} />}
                label="Section 5"
                title="Engagement & Clinical Summary"
                subtitle="Global interaction performance, continuity of engagement, and session efficiency indicators."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Overall Engagement Index</h3>
                                <p className="clinical-panel__subtitle">Composite clinician-facing engagement score from the current session summary.</p>
                            </div>
                        </div>

                        <EngagementGauge value={Math.round(record.total_engagement_summary.total_engagement_average * 100)} />
                    </article>

                    <article className="clinical-panel clinical-panel--stacked">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Clinical Summary</h3>
                                <p className="clinical-panel__subtitle">Session efficiency and continuity markers for quick review.</p>
                            </div>
                        </div>

                        <div className="clinical-tiles-grid">
                            <MetricTile label="Interaction Continuity" value={formatPercent(record.total_engagement_summary.interaction_continuity_score)} tone="green" />
                            <MetricTile label="Session Efficiency" value={`${record.total_engagement_summary.session_duration} min`} tone="blue" />
                            <MetricTile label="System Confidence" value={formatPercent(record.vision_session_stats.system_confidence)} />
                        </div>

                        <div className="clinical-summary-note">
                            <span className="clinical-summary-note__label">Clinical Impression</span>
                            <p className="clinical-summary-note__text">
                                Engagement remained stable through most of the session with sustained focus retention, high sensor confidence, and no excessive escalation markers.
                            </p>
                        </div>
                    </article>
                </div>
            </SectionBlock>

            <SectionBlock
                icon={<Sparkles size={18} strokeWidth={2.2} />}
                label="Section 6"
                title="Adaptive Reinforcement Intelligence"
                subtitle="Behavioral reinforcement effectiveness, intervention ranking, and preferred strategy performance over time."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Behavioral Reinforcement Effectiveness</h3>
                                <p className="clinical-panel__subtitle">Comparative performance of active reinforcement styles observed in structured interventions.</p>
                            </div>
                        </div>

                        <div className="reinforcement-comparison">
                            {reinforcementRanking.map((entry) => (
                                <div key={entry.key} className="reinforcement-comparison__row">
                                    <div className="reinforcement-comparison__meta">
                                        <span className="reinforcement-comparison__label">{entry.label}</span>
                                        <span className="reinforcement-comparison__value">{formatPercent(entry.score)}</span>
                                    </div>
                                    <div className="reinforcement-comparison__track">
                                        <div
                                            className={`reinforcement-comparison__fill ${entry.key === record.reinforcement_metrics.preferred_style ? 'is-preferred' : ''}`}
                                            style={{ width: `${Math.round(entry.score * 100)}%` }}
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </article>

                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Preferred Intervention Strategy</h3>
                                <p className="clinical-panel__subtitle">Primary reinforcement signal and strategy usage volume across recorded events.</p>
                            </div>
                        </div>

                        <div className="reinforcement-summary">
                            <div className="reinforcement-summary__hero">
                                <span className="reinforcement-summary__label">Best Performing Strategy</span>
                                <span className="reinforcement-summary__value">{bestStrategy.label}</span>
                                <span className="reinforcement-summary__caption">
                                    Preferred style recorded as {formatStyleLabel(record.reinforcement_metrics.preferred_style)}
                                </span>
                            </div>

                            <div className="clinical-tiles-grid">
                                <MetricTile label="Preferred Style" value={formatStyleLabel(record.reinforcement_metrics.preferred_style)} tone="green" />
                                <MetricTile label="Total Events" value={record.reinforcement_metrics.total_events} />
                            </div>

                            <ol className="reinforcement-ranking-list">
                                {reinforcementRanking.map((entry) => (
                                    <li key={entry.key} className="reinforcement-ranking-list__item">
                                        <span>{entry.label}</span>
                                        <span>{formatPercent(entry.score)}</span>
                                    </li>
                                ))}
                            </ol>
                        </div>
                    </article>
                </div>
            </SectionBlock>
        </>
    );
}
