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

export default function ClinicalStudentSections({ record, visionData }) {
    // 1. Data from 'emotional_metrics' table (Python Core / Dashboard MySQL)
    const stabilityIndex = getStabilityIndex(record.emotional_metrics);
    
    // 2. Data from 'reinforcement_metrics' table
    const reinforcementRanking = getReinforcementRanking(record.reinforcement_metrics);
    const bestStrategy = reinforcementRanking[0];
    
    // 3. Data from 'vision_metrics' and 'engagement_timeline' tables
    // Prioritize real visionData from the API if available, else fallback to mock
    const radarMetrics = [
        { label: 'Engage', value: visionData ? visionData.avg_engagement_score : record.vision_session_stats.avg_engagement_score },
        { label: 'Gaze', value: visionData ? visionData.avg_gaze_score : record.vision_session_stats.avg_gaze_score },
        { label: 'System', value: visionData ? visionData.system_confidence : record.vision_session_stats.system_confidence },
        { label: 'Face', value: visionData ? visionData.face_conf : record.perception_confidence.face_conf },
        { label: 'Gesture', value: visionData ? visionData.gesture_conf : record.perception_confidence.gesture_conf },
        { label: 'Object', value: visionData ? visionData.object_conf : record.perception_confidence.object_conf }
    ];

    const emotionalTrendChips = [
        record.emotional_metrics.frustration_count <= 8 ? 'Frustration within monitored range' : 'Escalation threshold elevated',
        record.emotional_metrics.recovery_count >= record.emotional_metrics.frustration_count ? 'Recovery exceeds disruption events' : 'Recovery below target response',
        record.emotional_metrics.neutral_stability_count >= 20 ? 'Baseline stability sustained' : 'Baseline variability noted'
    ];

    const vocalDistribution = [
        { label: 'Neutral', value: record.vocal_mood_distribution.neutral, tone: 'calm' },
        { label: 'Arousal', value: record.vocal_mood_distribution.arousal, tone: 'alert' },
        { label: 'Withdrawal', value: record.vocal_mood_distribution.withdrawal, tone: 'risk' }
    ];

    // 4. Data from 'learning_progress' and 'user_profiles' tables
    const masteryValue = record.learning_progress.mastery_level;
    const conceptName = record.learning_progress.concept_name;
    const instructionLevel = record.user_profiles.instruction_depth;

    return (
        <>
            <SectionBlock
                icon={<BrainCircuit size={18} strokeWidth={2.2} />}
                label="Section 1"
                title="Cognitive Development"
                subtitle="Progress from 'learning_progress' and 'user_profiles' tables."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Cognitive Mastery</h3>
                                <p className="clinical-panel__subtitle">Current acquisition profile for {conceptName}</p>
                            </div>
                        </div>

                        <div className="cognitive-panel">
                            <div className="cognitive-panel__chart-container">
                                <RadialMasteryChart value={masteryValue} />
                                <span className="cognitive-panel__chart-label">Mastery Level</span>
                            </div>

                            <div className="cognitive-panel__details">
                                <HorizontalBar
                                    label="Task Completion Reliability"
                                    value={formatPercent(record.learning_progress.success_rate)}
                                    percent={Math.round(record.learning_progress.success_rate * 100)}
                                    tone="blue"
                                />
                                <div className="clinical-tiles-grid">
                                    <MetricTile label="Total Attempts" value={record.learning_progress.attempt_count} />
                                    <MetricTile label="Active Concept" value={conceptName} tone="green" />
                                </div>
                            </div>
                        </div>
                    </article>

                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Instructional Profile</h3>
                                <p className="clinical-panel__subtitle">Derived from user profiles.</p>
                            </div>
                        </div>

                        <div className="profile-panel">
                            <div className="profile-panel__group">
                                <span className="profile-panel__label">Instruction Complexity</span>
                                <div className="profile-panel__complexity-card">
                                    <span className="profile-panel__complexity-value">Level {instructionLevel}</span>
                                    <span className="profile-panel__complexity-caption">Based on user_profiles.instruction_depth</span>
                                </div>
                            </div>
                            <div className="profile-panel__group">
                                <span className="profile-panel__label">Preferred Topics</span>
                                <div className="profile-panel__chips">
                                    {record.user_profiles.preferred_topics.map((topic) => (
                                        <span key={topic} className="profile-panel__chip">{topic}</span>
                                    ))}
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
                subtitle="Real-time analytics from 'emotional_metrics' and 'zpd_metrics' tables."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Emotional Regulation</h3>
                                <p className="clinical-panel__subtitle">Distribution from the emotional_metrics table.</p>
                            </div>
                        </div>

                        <EmotionStack data={record.emotional_metrics} />

                        <div className="clinical-trend-chips">
                            {emotionalTrendChips.map((chip) => (
                                <span key={chip} className="clinical-trend-chip">{chip}</span>
                            ))}
                        </div>
                    </article>

                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Regulation Index</h3>
                                <p className="clinical-panel__subtitle">Calculated Stability Index.</p>
                            </div>
                        </div>

                        <StabilityMeter value={stabilityIndex} />

                        <div className="clinical-tiles-grid">
                            <MetricTile label="Frustration" value={record.emotional_metrics.frustration_count} tone="risk" />
                            <MetricTile label="Recovery" value={record.emotional_metrics.recovery_count} tone="green" />
                            <MetricTile label="Neutral" value={record.emotional_metrics.neutral_stability_count} tone="blue" />
                        </div>
                    </article>
                </div>
            </SectionBlock>

            <SectionBlock
                icon={<Eye size={18} strokeWidth={2.2} />}
                label="Section 3"
                title="Vision & Perception Analysis"
                subtitle="Data from 'vision_sessions', 'vision_metrics', and 'engagement_timeline' tables."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Visual Engagement Radar</h3>
                                <p className="clinical-panel__subtitle">Multimodal perception summary.</p>
                            </div>
                        </div>

                        <RadarChart metrics={radarMetrics} />
                    </article>

                    <article className="clinical-panel">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Behavioral Signals</h3>
                                <p className="clinical-panel__subtitle">Focus and Distraction counts from vision_metrics.</p>
                            </div>
                        </div>

                        <div className="confidence-stack">
                            <HorizontalBar label="Presence Confidence" value={formatPercent(visionData ? visionData.face_conf : record.perception_confidence.face_conf)} percent={Math.round((visionData ? visionData.face_conf : record.perception_confidence.face_conf) * 100)} tone="green" />
                            <HorizontalBar label="Gesture Active" value={formatPercent(visionData ? visionData.gesture_conf : record.perception_confidence.gesture_conf)} percent={Math.round((visionData ? visionData.gesture_conf : record.perception_confidence.gesture_conf) * 100)} tone="blue" />
                        </div>

                        <AttentionTimeline
                            focusedDuration={visionData ? visionData.focused_duration : record.vision_behavior_counts.focused_duration}
                            sessionDuration={record.total_engagement_summary.session_duration}
                            distractionFrames={visionData ? visionData.distraction_frames : record.vision_behavior_counts.distraction_frames}
                        />

                        <div className="clinical-tiles-grid">
                            <MetricTile label="Avg Engagement" value={formatPercent(visionData ? visionData.avg_engagement_score : record.vision_session_stats.avg_engagement_score)} tone="blue" />
                            <MetricTile label="Visual Focus" value={formatPercent(visionData ? visionData.avg_gaze_score : record.vision_session_stats.avg_gaze_score)} tone="blue" />
                            <MetricTile label="Focus (Min)" value={`${visionData ? visionData.focused_duration : record.vision_behavior_counts.focused_duration}m`} tone="green" />
                        </div>
                    </article>
                </div>
            </SectionBlock>

            <SectionBlock
                icon={<Sparkles size={18} strokeWidth={2.2} />}
                label="Section 4"
                title="Adaptive Reinforcement Intelligence"
                subtitle="Performance data from 'reinforcement_metrics' table."
            >
                <div className="clinical-section-grid clinical-section-grid--two-column">
                    <article className="clinical-panel clinical-panel--wide">
                        <div className="clinical-panel__header">
                            <div>
                                <h3 className="clinical-panel__title">Strategy Effectiveness</h3>
                                <p className="clinical-panel__subtitle">Comparative performance from reinforcement_metrics.</p>
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
                                <h3 className="clinical-panel__title">Preferred Pathway</h3>
                                <p className="clinical-panel__subtitle">Top reinforcement style.</p>
                            </div>
                        </div>

                        <div className="reinforcement-summary">
                            <div className="reinforcement-summary__hero">
                                <span className="reinforcement-summary__label">Optimal Strategy</span>
                                <span className="reinforcement-summary__value">{bestStrategy.label}</span>
                                <span className="reinforcement-summary__caption">
                                    Based on {record.reinforcement_metrics.total_events} recorded events
                                </span>
                            </div>

                            <div className="clinical-tiles-grid">
                                <MetricTile label="Total Events" value={record.reinforcement_metrics.total_events} />
                                <MetricTile label="Style" value={bestStrategy.label} tone="green" />
                            </div>
                        </div>
                    </article>
                </div>
            </SectionBlock>
        </>
    );
}
