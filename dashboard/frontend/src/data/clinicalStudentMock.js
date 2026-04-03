function seededRandom(seed) {
    const x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
}

export function getSeededMock(childId, childData = {}) {
    const seed = parseInt(childId) || 123;
    const r = (val, range = 0.2) => {
        const rand = seededRandom(seed + val.length);
        return val + (rand * range * 2 - range);
    };

    return {
        patient: {
            name: childData.name || 'Student Name',
            age: childData.age || 6,
            id: childId,
            lastInteractionLabel: childData.lastSessionDate || 'April 2, 2026'
        },
        learning_progress: {
            concept_name: 'Counting',
            mastery_level: Math.floor(seededRandom(seed + 1) * 3) + 2,
            attempt_count: Math.floor(seededRandom(seed + 2) * 20) + 15,
            success_rate: 0.6 + (seededRandom(seed + 3) * 0.3)
        },
        emotional_metrics: {
            frustration_count: Math.floor(seededRandom(seed + 4) * 10) + 5,
            recovery_count: Math.floor(seededRandom(seed + 5) * 12) + 8,
            neutral_stability_count: Math.floor(seededRandom(seed + 6) * 15) + 20
        },
        user_profiles: {
            preferred_topics: ['Animals', 'Blocks', 'Colors'],
            instruction_depth: Math.floor(seededRandom(seed + 7) * 2) + 1
        },
        reinforcement_metrics: {
            calm_validation: 0.7 + (seededRandom(seed + 8) * 0.2),
            praise_based: 0.6 + (seededRandom(seed + 9) * 0.3),
            achievement_based: 0.5 + (seededRandom(seed + 10) * 0.4),
            playful: 0.5 + (seededRandom(seed + 11) * 0.3),
            preferred_style: 'calm_validation',
            total_events: Math.floor(seededRandom(seed + 12) * 30) + 30
        },
        vision_session_stats: {
            avg_engagement_score: 0.7 + (seededRandom(seed + 13) * 0.25),
            avg_gaze_score: 0.65 + (seededRandom(seed + 14) * 0.3),
            system_confidence: 0.85 + (seededRandom(seed + 15) * 0.1)
        },
        vision_behavior_counts: {
            distraction_frames: Math.floor(seededRandom(seed + 16) * 25) + 10,
            focused_duration: 10 + (seededRandom(seed + 17) * 8)
        },
        perception_confidence: {
            face_conf: 0.88 + (seededRandom(seed + 18) * 0.1),
            gesture_conf: 0.8 + (seededRandom(seed + 19) * 0.15),
            object_conf: 0.75 + (seededRandom(seed + 20) * 0.2)
        },
        voice_prosody_metrics: {
            speaking_rate: Math.floor(seededRandom(seed + 21) * 40) + 90,
            volume: 0.5 + (seededRandom(seed + 22) * 0.3),
            stability_score: 0.7 + (seededRandom(seed + 23) * 0.2)
        },
        vocal_mood_distribution: {
            neutral: 0.55 + (seededRandom(seed + 24) * 0.2),
            arousal: 0.15 + (seededRandom(seed + 25) * 0.15),
            withdrawal: 0.1 + (seededRandom(seed + 26) * 0.15)
        },
        total_engagement_summary: {
            total_engagement_average: 0.7 + (seededRandom(seed + 27) * 0.2),
            interaction_continuity_score: 0.75 + (seededRandom(seed + 28) * 0.15),
            session_duration: 15 + (seededRandom(seed + 29) * 10)
        }
    };
}

export const clinicalStudentMock = getSeededMock('102', { name: 'Leo Smith', age: 6 });

export function formatPercent(value) {
    return `${Math.round(value * 100)}%`;
}

export function formatStyleLabel(style) {
    return style
        .split('_')
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(' ');
}

export function getStabilityIndex(data) {
    const total = data.frustration_count + data.recovery_count + data.neutral_stability_count;
    if (!total) {
        return 0;
    }

    return Math.round(((data.recovery_count + data.neutral_stability_count) / total) * 100);
}

export function getReinforcementRanking(data) {
    return [
        { key: 'calm_validation', score: data.calm_validation },
        { key: 'praise_based', score: data.praise_based },
        { key: 'achievement_based', score: data.achievement_based },
        { key: 'playful', score: data.playful }
    ]
        .map((item) => ({
            ...item,
            label: formatStyleLabel(item.key)
        }))
        .sort((left, right) => right.score - left.score);
}

export function getClinicalReports(record) {
    const stabilityIndex = getStabilityIndex(record.emotional_metrics);
    const ranking = getReinforcementRanking(record.reinforcement_metrics);
    const topStrategy = ranking[0];

    return [
        {
            id: 'cognitive-progress',
            title: 'Diagnostic Cognitive Progress Evaluation',
            summary: 'Comprehensive evaluation of longitudinal concept acquisition, task completion reliability, and cognitive fatigue markers during structured intervention activities.',
            metrics: [
                `Mastery Level: ${record.learning_progress.mastery_level}/5`,
                `Completion Reliability: ${formatPercent(record.learning_progress.success_rate)}`,
                `Total Trials Attempted: ${record.learning_progress.attempt_count}`,
                `Target Domain: ${record.learning_progress.concept_name}`
            ],
            lines: [
                `PATIENT EVALUATION RECORD - STRICTLY CONFIDENTIAL`,
                `--------------------------------------------------`,
                `Patient Name: ${record.patient.name}`,
                `Medical Record / ID: #${record.patient.id}`,
                `Date of Last Interaction: ${record.patient.lastInteractionLabel}`,
                `--------------------------------------------------`,
                `COGNITIVE PROGRESS SUMMARY`,
                `Focus Domain: ${record.learning_progress.concept_name}`,
                `Current Diagnostic Mastery Level: ${record.learning_progress.mastery_level} of 5`,
                `Task Completion Reliability Index: ${formatPercent(record.learning_progress.success_rate)}`,
                `Cumulative Intervention Trials: ${record.learning_progress.attempt_count}`,
                ``,
                `CLINICIAN OBSERVATIONS & INTERPRETATION:`,
                `Patient exhibits positive acquisition vectors within the target domain. Concept retention is progressing favorably with consistent task completion.`
            ]
        },
        {
            id: 'emotional-regulation',
            title: 'Emotional Regulation & Dysregulation Report',
            summary: 'Detailed analysis of emotional baseline stability, sensory frustration thresholds, and self-directed recovery mechanisms observed across recent sessions.',
            metrics: [
                `Baseline Stability Index: ${stabilityIndex}%`,
                `Frustration Events Observed: ${record.emotional_metrics.frustration_count}`,
                `Successful Recoveries: ${record.emotional_metrics.recovery_count}`,
                `Neutral Baseline Periods: ${record.emotional_metrics.neutral_stability_count}`
            ],
            lines: [
                `PATIENT EVALUATION RECORD - STRICTLY CONFIDENTIAL`,
                `--------------------------------------------------`,
                `Patient Name: ${record.patient.name}`,
                `Medical Record / ID: #${record.patient.id}`,
                `--------------------------------------------------`,
                `AFFECT & EMOTIONAL REGULATION SUMMARY`,
                `Observable Frustration Events: ${record.emotional_metrics.frustration_count}`,
                `Successful Recovery Transitions: ${record.emotional_metrics.recovery_count}`,
                `Clinically Stable Baseline Periods: ${record.emotional_metrics.neutral_stability_count}`,
                `Calculated Stability Index: ${stabilityIndex}%`,
                ``,
                `CLINICIAN OBSERVATIONS & INTERPRETATION:`,
                `Recovery mechanics remain stronger than emotional escalation. Patient demonstrates capacity to return to a stable neutral baseline following minor behavioral dysregulation.`
            ]
        },
        {
            id: 'engagement-analysis',
            title: 'Multimodal Attention & Engagement Analysis',
            summary: 'Clinical assessment of joint attention, sustained focus retention, and interaction continuity utilizing computer vision symptomatic tracking.',
            metrics: [
                `Overall Engagement Quotient: ${formatPercent(record.total_engagement_summary.total_engagement_average)}`,
                `Interaction Continuity: ${formatPercent(record.total_engagement_summary.interaction_continuity_score)}`,
                `Sustained Focus Duration: ${Math.round(record.vision_behavior_counts.focused_duration)} min`,
                `Distraction Frequency: ${record.vision_behavior_counts.distraction_frames} instances`
            ],
            lines: [
                `PATIENT EVALUATION RECORD - STRICTLY CONFIDENTIAL`,
                `--------------------------------------------------`,
                `Patient Name: ${record.patient.name}`,
                `Medical Record / ID: #${record.patient.id}`,
                `--------------------------------------------------`,
                `COMPREHENSIVE ENGAGEMENT & ATTENTION SUMMARY`,
                `Overall Engagement Quotient: ${formatPercent(record.total_engagement_summary.total_engagement_average)}`,
                `Interaction Continuity Index: ${formatPercent(record.total_engagement_summary.interaction_continuity_score)}`,
                `Sustained Visual Attention (Gaze Score): ${formatPercent(record.vision_session_stats.avg_gaze_score)}`,
                `Focus Retention Duration: ${Math.round(record.vision_behavior_counts.focused_duration)} minutes`,
                `Recorded Distraction Instances: ${record.vision_behavior_counts.distraction_frames}`,
                ``,
                `CLINICIAN OBSERVATIONS & INTERPRETATION:`,
                `Sustained engagement metrics remain clinically acceptable. Visual attention correlates strongly with interactive milestones, with manageable distraction frequency.`
            ]
        },
        {
            id: 'session-summary',
            title: 'Comprehensive Session & Pathway Summary',
            summary: 'Integrative evaluation of behavioral reinforcement efficacy, vocal prosody stability, and preferred intervention pathways for the current observation period.',
            metrics: [
                `Primary Intervention Pathway: ${formatStyleLabel(record.reinforcement_metrics.preferred_style)}`,
                `Behavioral Reinforcement Efficacy: ${formatPercent(topStrategy.score)}`,
                `Vocal Prosody Stability: ${formatPercent(record.voice_prosody_metrics.stability_score)}`,
                `Diagnostic Sensor Confidence: ${formatPercent(record.vision_session_stats.system_confidence)}`
            ],
            lines: [
                `PATIENT EVALUATION RECORD - STRICTLY CONFIDENTIAL`,
                `--------------------------------------------------`,
                `Patient Name: ${record.patient.name}`,
                `Medical Record / ID: #${record.patient.id}`,
                `Total Session Duration: ${Math.round(record.total_engagement_summary.session_duration)} minutes`,
                `--------------------------------------------------`,
                `CLINICAL PATHWAY & BEHAVIORAL REINFORCEMENT SUMMARY`,
                `Primary Intervention Pathway: ${formatStyleLabel(record.reinforcement_metrics.preferred_style)}`,
                `Behavioral Reinforcement Efficacy: ${formatPercent(topStrategy.score)}`,
                `Total Behavioral Events Recorded: ${record.reinforcement_metrics.total_events}`,
                ``,
                `BIOMETRIC DIAGNOSTIC CONFIDENCE`,
                `Vocal Prosody Stability: ${formatPercent(record.voice_prosody_metrics.stability_score)}`,
                `Sensor Confidence / Validity Index: ${formatPercent(record.vision_session_stats.system_confidence)}`,
                `Vocal Affect Distribution: Neutral ${formatPercent(record.vocal_mood_distribution.neutral)}, Arousal ${formatPercent(record.vocal_mood_distribution.arousal)}, Withdrawal ${formatPercent(record.vocal_mood_distribution.withdrawal)}`,
                ``,
                `CLINICIAN OBSERVATIONS & INTERPRETATION:`,
                `${formatStyleLabel(record.reinforcement_metrics.preferred_style)} remains the leading effective intervention pattern. Visual and vocal biometric readings maintain high diagnostic validity.`
            ]
        }
    ];
}
