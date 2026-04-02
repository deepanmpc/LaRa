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
            title: 'Cognitive Progress Report',
            summary: 'Mastery trend, concept acquisition, and completion reliability for the current intervention target.',
            metrics: [
                `Cognitive Mastery ${record.learning_progress.mastery_level}/5`,
                `Task Completion Reliability ${formatPercent(record.learning_progress.success_rate)}`,
                `Learning Attempts ${record.learning_progress.attempt_count}`
            ],
            lines: [
                `Patient: ${record.patient.name}`,
                `Record ID: #${record.patient.id}`,
                `Concept Acquisition: ${record.learning_progress.concept_name}`,
                `Cognitive Mastery: ${record.learning_progress.mastery_level} of 5`,
                `Task Completion Reliability: ${formatPercent(record.learning_progress.success_rate)}`,
                `Learning Attempts: ${record.learning_progress.attempt_count}`,
                'Clinical interpretation: Concept retention is progressing with consistent task completion.'
            ]
        },
        {
            id: 'emotional-regulation',
            title: 'Emotional Regulation Report',
            summary: 'Observed frustration, recovery, and baseline stability patterns across recent clinician-reviewed interactions.',
            metrics: [
                `Stability Index ${stabilityIndex}%`,
                `Frustration Frequency ${record.emotional_metrics.frustration_count}`,
                `Recovery Efficiency ${record.emotional_metrics.recovery_count}`
            ],
            lines: [
                `Patient: ${record.patient.name}`,
                `Record ID: #${record.patient.id}`,
                `Frustration Frequency: ${record.emotional_metrics.frustration_count}`,
                `Recovery Efficiency: ${record.emotional_metrics.recovery_count}`,
                `Baseline Stability: ${record.emotional_metrics.neutral_stability_count}`,
                `Stability Index: ${stabilityIndex}%`,
                'Clinical interpretation: Recovery remains stronger than frustration escalation, with stable neutral baseline periods.'
            ]
        },
        {
            id: 'engagement-analysis',
            title: 'Engagement Analysis Report',
            summary: 'Multimodal engagement, focus retention, visual attention, and interaction continuity summary.',
            metrics: [
                `Overall Engagement Index ${formatPercent(record.total_engagement_summary.total_engagement_average)}`,
                `Interaction Continuity ${formatPercent(record.total_engagement_summary.interaction_continuity_score)}`,
                `Focus Retention ${record.vision_behavior_counts.focused_duration} min`
            ],
            lines: [
                `Patient: ${record.patient.name}`,
                `Record ID: #${record.patient.id}`,
                `Overall Engagement Index: ${formatPercent(record.total_engagement_summary.total_engagement_average)}`,
                `Interaction Continuity: ${formatPercent(record.total_engagement_summary.interaction_continuity_score)}`,
                `Visual Attention: ${formatPercent(record.vision_session_stats.avg_gaze_score)}`,
                `Focus Retention: ${record.vision_behavior_counts.focused_duration} minutes`,
                `Distraction Frames: ${record.vision_behavior_counts.distraction_frames}`,
                'Clinical interpretation: Sustained engagement remains clinically acceptable with manageable distraction frequency.'
            ]
        },
        {
            id: 'session-summary',
            title: 'Session Summary Report',
            summary: 'Voice, perception, reinforcement effectiveness, and intervention preference summary for clinician review.',
            metrics: [
                `Preferred Intervention ${formatStyleLabel(record.reinforcement_metrics.preferred_style)}`,
                `Speech Stability ${formatPercent(record.voice_prosody_metrics.stability_score)}`,
                `Sensor Confidence ${formatPercent(record.vision_session_stats.system_confidence)}`
            ],
            lines: [
                `Patient: ${record.patient.name}`,
                `Record ID: #${record.patient.id}`,
                `Session Duration: ${record.total_engagement_summary.session_duration} minutes`,
                `Preferred Intervention Strategy: ${formatStyleLabel(record.reinforcement_metrics.preferred_style)}`,
                `Behavioral Reinforcement Effectiveness: ${formatPercent(topStrategy.score)}`,
                `Speech Stability: ${formatPercent(record.voice_prosody_metrics.stability_score)}`,
                `Sensor Confidence: ${formatPercent(record.vision_session_stats.system_confidence)}`,
                `Voice Mood Distribution: Neutral ${formatPercent(record.vocal_mood_distribution.neutral)}, Arousal ${formatPercent(record.vocal_mood_distribution.arousal)}, Withdrawal ${formatPercent(record.vocal_mood_distribution.withdrawal)}`,
                'Clinical interpretation: Calm validation remains the leading intervention pattern with stable vocal and visual read quality.'
            ]
        }
    ];
}
