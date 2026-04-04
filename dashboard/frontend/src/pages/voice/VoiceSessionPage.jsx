/**
 * VoiceSessionPage — Live WebSocket-connected session UI
 *
 * Fixes in this version:
 *  1. Stop works — sends session_stop and immediately shows summary
 *  2. Session summary overlay on end with full stats + mood breakdown
 *  3. Proper layout — balanced, no oversized speech text, indicators fixed-height
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LaraAvatar from '../../components/voice/LaraAvatar';
import ListeningIndicator from '../../components/voice/ListeningIndicator';
import ThinkingIndicator from '../../components/voice/ThinkingIndicator';

const WS_URL = 'ws://localhost:8765';
const RECONNECT_DELAY_MS = 2000;
const MAX_RECONNECT_ATTEMPTS = 10;

const MOOD_COLORS = {
    happy:      { bg: '#f0fdf4', text: '#16a34a', dot: '#22c55e' },
    neutral:    { bg: '#f8fafc', text: '#64748b', dot: '#94a3b8' },
    frustrated: { bg: '#fff7ed', text: '#c2410c', dot: '#f97316' },
    sad:        { bg: '#eff6ff', text: '#1d4ed8', dot: '#60a5fa' },
    anxious:    { bg: '#fdf4ff', text: '#7e22ce', dot: '#c084fc' },
    quiet:      { bg: '#f8fafc', text: '#64748b', dot: '#94a3b8' },
};
const moodColor = (m) => MOOD_COLORS[m] ?? MOOD_COLORS.neutral;

const VISION_ATTENTION_COLORS = {
    FOCUSED:     { bg: '#f0fdf4', text: '#166534', dot: '#22c55e' },
    DISTRACTED:  { bg: '#fffbeb', text: '#b45309', dot: '#f59e0b' },
    ABSENT:      { bg: '#fef2f2', text: '#b91c1c', dot: '#ef4444' },
    UNKNOWN:     { bg: '#f8fafc', text: '#64748b', dot: '#94a3b8' },
};
const visionAttentionColor = (state) => VISION_ATTENTION_COLORS[state] ?? VISION_ATTENTION_COLORS.UNKNOWN;

const VISION_ALERT_COLORS = {
    distraction:    { bg: '#fffbeb', border: '#fcd34d', text: '#b45309' },
    absence:        { bg: '#fef2f2', border: '#fca5a5', text: '#b91c1c' },
    low_engagement: { bg: '#fff7ed', border: '#fdba74', text: '#c2410c' },
    vision_alert:   { bg: '#fff7ed', border: '#fdba74', text: '#c2410c' },
};
const visionAlertColor = (type) => VISION_ALERT_COLORS[type] ?? VISION_ALERT_COLORS.vision_alert;

const VoiceSessionPage = () => {
    const { childId, sessionUuid } = useParams();
    const navigate = useNavigate();

    const [voiceState, setVoiceState]     = useState('idle');
    const [speechText, setSpeechText]     = useState('');
    const [transcript, setTranscript]     = useState([]);
    const [sessionState, setSessionState] = useState('waiting');
    const [turnCount, setTurnCount]       = useState(0);
    const [difficulty, setDifficulty]     = useState(2);
    const [mood, setMood]                 = useState('neutral');
    const [moodConf, setMoodConf]         = useState(0.0);
    const [strategy, setStrategy]         = useState('neutral');
    const [sessionDuration, setSessionDuration] = useState(0);
    const [summary, setSummary]           = useState(null);
    const [showSummary, setShowSummary]   = useState(false);
    const [wsStatus, setWsStatus]         = useState('connecting');
    const [reconnectCount, setReconnectCount] = useState(0);
    const [visionState, setVisionState]   = useState(null);
    const [visionAlert, setVisionAlert]   = useState(null);
    const [lastGesture, setLastGesture]   = useState(null);

    const wsRef               = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const reconnectCountRef   = useRef(0);
    const transcriptEndRef    = useRef(null);
    const sessionStartTimeRef = useRef(null);
    const durationTimerRef    = useRef(null);
    const moodHistoryRef      = useRef([]);
    const difficultyPeakRef   = useRef(2);
    const laraCountRef        = useRef(0);
    const childCountRef       = useRef(0);
    // Keep live refs for use inside buildSummary without stale closure
    const turnCountRef        = useRef(0);
    const difficultyRef       = useRef(2);
    const moodRef             = useRef('neutral');
    const sessionDurationRef  = useRef(0);
    const moodConfRef         = useRef(0.0);
    const visionAlertTimerRef = useRef(null);
    const gestureTimerRef     = useRef(null);

    const formatDuration = (secs) => {
        const m = Math.floor(secs / 60).toString().padStart(2, '0');
        const s = (secs % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [transcript]);

    useEffect(() => {
        if (sessionState === 'active') {
            sessionStartTimeRef.current = Date.now();
            durationTimerRef.current = setInterval(() => {
                const d = Math.floor((Date.now() - sessionStartTimeRef.current) / 1000);
                setSessionDuration(d);
                sessionDurationRef.current = d;
            }, 1000);
        } else {
            clearInterval(durationTimerRef.current);
        }
        return () => clearInterval(durationTimerRef.current);
    }, [sessionState]);

    const buildSummary = useCallback(() => {
        const hist = moodHistoryRef.current;
        const moodCounts = hist.reduce((acc, m) => { acc[m] = (acc[m] || 0) + 1; return acc; }, {});
        const total = hist.length;
        const positiveTurns = hist.filter(m => m === 'happy' || m === 'neutral').length;
        const engagementPct = total > 0 ? Math.round((positiveTurns / total) * 100) : 0;
        return {
            duration: sessionDurationRef.current,
            turns: turnCountRef.current,
            difficultyReached: difficultyPeakRef.current,
            dominantMood: Object.entries(moodCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? 'neutral',
            engagementPct,
            laraResponses: laraCountRef.current,
            childUtterances: childCountRef.current,
            moodBreakdown: moodCounts,
        };
    }, []);

    const endSession = useCallback(async () => {
        clearInterval(durationTimerRef.current);
        setSessionState('ended');
        setVoiceState('idle');
        clearTimeout(visionAlertTimerRef.current);
        clearTimeout(gestureTimerRef.current);
        setVisionAlert(null);
        setLastGesture(null);
        const s = buildSummary();
        setSummary(s);
        localStorage.removeItem(`activeSession_${childId}`);
        setShowSummary(true);

        try {
            const token = localStorage.getItem('token');
            await fetch('/api/family/session/end', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': token ? `Bearer ${token}` : ''
                },
                body: JSON.stringify({
                    sessionUuid: sessionUuid,
                    childIdHashed: childId,
                    durationSeconds: s.duration,
                    avgMoodConfidence: moodConfRef.current,
                    totalInterventions: s.laraResponses
                })
            });
        } catch (err) {
            console.error('[VoiceSession] Persistence Error:', err);
        }
    }, [buildSummary, sessionUuid, childId]);

    const handleMessage = useCallback((event) => {
        let msg;
        try { msg = JSON.parse(event.data); } catch { return; }

        switch (msg.type) {
            case 'system_state':
                setVoiceState(msg.mode === 'resting' ? 'idle' : msg.mode);
                if (msg.turn_count !== undefined) {
                    setTurnCount(msg.turn_count);
                    turnCountRef.current = msg.turn_count;
                }
                if (msg.difficulty !== undefined) {
                    setDifficulty(msg.difficulty);
                    difficultyRef.current = msg.difficulty;
                    if (msg.difficulty > difficultyPeakRef.current) difficultyPeakRef.current = msg.difficulty;
                }
                if (msg.mode !== 'speaking') setTimeout(() => setSpeechText(''), 1500);
                break;

            case 'session_ack':
                if (msg.status === 'starting')        setSessionState('active');
                else if (msg.status === 'stopping') {
                    reconnectCountRef.current = 0;
                    setReconnectCount(0);
                    endSession();
                }
                else if (msg.status === 'already_running') setSessionState('active');
                else if (msg.status === 'not_running')     setSessionState('waiting');
                break;

            case 'transcript':
                if (msg.speaker === 'child') childCountRef.current += 1;
                setTranscript(prev => [...prev, { speaker: msg.speaker, text: msg.text, timestamp: msg.timestamp }]);
                break;

            case 'lara_response': {
                laraCountRef.current += 1;
                setSpeechText(msg.text);
                const newMood = msg.mood ?? 'neutral';
                setMood(newMood);
                moodRef.current = newMood;
                const newConf = msg.mood_confidence ?? 0.0;
                setMoodConf(newConf);
                moodConfRef.current = newConf;
                setStrategy(msg.strategy ?? 'neutral');
                if (msg.mood) moodHistoryRef.current.push(msg.mood);
                setTranscript(prev => [...prev, { speaker: 'lara', text: msg.text, timestamp: Date.now() / 1000 }]);
                break;
            }

            case 'mood_update':
                setMood(msg.mood);
                moodRef.current = msg.mood;
                setMoodConf(msg.confidence);
                moodConfRef.current = msg.confidence;
                if (msg.mood) moodHistoryRef.current.push(msg.mood);
                break;

            case 'difficulty_change':
                setDifficulty(msg.new_difficulty);
                difficultyRef.current = msg.new_difficulty;
                if (msg.new_difficulty > difficultyPeakRef.current) difficultyPeakRef.current = msg.new_difficulty;
                break;

            case 'vision_update': {
                setVisionState({
                    presence: msg.presence,
                    attention: msg.attentionState,
                    engagement: msg.engagementScore,
                    gesture: msg.gesture,
                    distractionFrames: msg.distractionFrames,
                });
                break;
            }

            case 'vision_alert': {
                setVisionAlert({ type: msg.alertType ?? msg.type, message: msg.message });
                clearTimeout(visionAlertTimerRef.current);
                visionAlertTimerRef.current = setTimeout(() => setVisionAlert(null), 4000);
                break;
            }

            case 'vision_gesture': {
                setLastGesture({ gesture: msg.gesture, ts: msg.timestamp });
                clearTimeout(gestureTimerRef.current);
                gestureTimerRef.current = setTimeout(() => setLastGesture(null), 2000);
                break;
            }

            case 'session_ended':
                endSession();
                break;

            case 'error':
                console.error('[LaRa Bridge] Pipeline error:', msg.message);
                break;

            default: break;
        }
    }, [endSession]);

    const mountedRef = useRef(true);

    const connect = useCallback(function connectSocket() {
        if (!mountedRef.current) return;
        if (reconnectCountRef.current >= MAX_RECONNECT_ATTEMPTS) { setWsStatus('error'); return; }
        // Close any existing connection first
        if (wsRef.current) {
            wsRef.current.onclose = null;
            wsRef.current.onerror = null;
            wsRef.current.onmessage = null;
            wsRef.current.close();
            wsRef.current = null;
        }
        setWsStatus('connecting');
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;
        ws.onopen = () => {
            if (!mountedRef.current) { ws.close(); return; }
            setWsStatus('connected'); reconnectCountRef.current = 0; setReconnectCount(0);
        };
        ws.onmessage = handleMessage;
        ws.onclose = () => {
            if (!mountedRef.current) return;
            setWsStatus('disconnected');
            reconnectCountRef.current += 1;
            setReconnectCount(reconnectCountRef.current);
            if (reconnectCountRef.current < MAX_RECONNECT_ATTEMPTS)
                reconnectTimeoutRef.current = setTimeout(connectSocket, RECONNECT_DELAY_MS);
            else setWsStatus('error');
        };
        ws.onerror = () => ws.close();
    }, [handleMessage]);

    useEffect(() => {
        mountedRef.current = true;
        connect();
        return () => {
            mountedRef.current = false;
            clearTimeout(reconnectTimeoutRef.current);
            if (wsRef.current) {
                wsRef.current.onclose = null;
                wsRef.current.onerror = null;
                wsRef.current.onmessage = null;
                wsRef.current.close();
                wsRef.current = null;
            }
            clearTimeout(visionAlertTimerRef.current);
            clearTimeout(gestureTimerRef.current);
        };
    }, [connect]);

    const sendCommand = (type) => {
        if (wsRef.current?.readyState === WebSocket.OPEN)
            wsRef.current.send(JSON.stringify({ type }));
    };

    const resetCounters = () => {
        moodHistoryRef.current = [];
        difficultyPeakRef.current = 2;
        laraCountRef.current = 0;
        childCountRef.current = 0;
        turnCountRef.current = 0;
        difficultyRef.current = 2;
        sessionDurationRef.current = 0;
    };

    const handleStartSession = () => {
        if (wsStatus !== 'connected') return;
        resetCounters();
        setSummary(null);
        setShowSummary(false);
        setTranscript([]);
        setSpeechText('');
        setSessionDuration(0);
        setTurnCount(0);
        setDifficulty(2);
        setMood('neutral');
        setMoodConf(0.0);
        setStrategy('neutral');
        setVisionState(null);
        setVisionAlert(null);
        setLastGesture(null);
        clearTimeout(visionAlertTimerRef.current);
        clearTimeout(gestureTimerRef.current);
        setSessionState('starting');
        sendCommand('session_start');
    };

    const handleStopSession = () => {
        // Send stop to Python — also end locally immediately so UI is responsive
        sendCommand('session_stop');
        endSession();
    };

    const statusColors = { connecting: '#f59e0b', connected: '#10b981', disconnected: '#ef4444', error: '#ef4444' };
    const statusLabels = {
        connecting:   'Connecting…',
        connected:    'Connected',
        disconnected: `Reconnecting… (${reconnectCount}/${MAX_RECONNECT_ATTEMPTS})`,
        error:        'Cannot reach LaRa',
    };

    const mc = moodColor(mood);
    const liveVision = visionState ?? {
        presence: false,
        attention: 'UNKNOWN',
        engagement: 0,
        gesture: 'NONE',
        distractionFrames: 0,
    };
    const attentionColors = visionAttentionColor(liveVision.attention);
    const alertColors = visionAlert ? visionAlertColor(visionAlert.type) : null;
    const gestureLabel = lastGesture?.gesture ? lastGesture.gesture.replace(/_/g, ' ') : '';

    return (
        <div style={{
            position: 'fixed', inset: 0, display: 'flex',
            background: '#eef4ff', fontFamily: "'Inter', Arial, sans-serif",
            overflow: 'hidden',
        }}>

            {/* ══ LEFT PANEL ══ */}
            <div style={{
                flex: 1, display: 'flex', flexDirection: 'column',
                alignItems: 'center', justifyContent: 'space-between',
                padding: '20px 28px 24px', minWidth: 0, gap: 8,
            }}>

                {/* Top bar */}
                <div style={{ width: '100%', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexShrink: 0 }}>
                    <div style={{
                        display: 'flex', alignItems: 'center', gap: 6,
                        background: 'white', borderRadius: 20, padding: '5px 13px',
                        boxShadow: '0 1px 5px rgba(0,0,0,0.07)', fontSize: 12,
                        color: statusColors[wsStatus], fontWeight: 600,
                    }}>
                        <div style={{ width: 6, height: 6, borderRadius: '50%', background: statusColors[wsStatus], animation: wsStatus === 'connected' ? 'pulse 2s infinite' : 'none' }} />
                        {statusLabels[wsStatus]}
                    </div>

                    <div style={{ display: 'flex', gap: 8 }}>
                        {sessionState === 'active' && (
                            <>
                                <div style={{
                                    display: 'flex', alignItems: 'center', gap: 5,
                                    background: mc.bg, border: `1px solid ${mc.dot}44`,
                                    borderRadius: 20, padding: '5px 11px', fontSize: 11, fontWeight: 600, color: mc.text, textTransform: 'capitalize',
                                }}>
                                    <div style={{ width: 5, height: 5, borderRadius: '50%', background: mc.dot }} />
                                    {mood} {Math.round(moodConf * 100)}%
                                </div>
                                <div style={{
                                    display: 'flex', alignItems: 'center', gap: 5,
                                    background: '#f0fdf4', border: '1px solid #bbf7d0',
                                    borderRadius: 20, padding: '5px 12px', fontSize: 11, fontWeight: 700, color: '#16a34a',
                                }}>
                                    <div style={{ width: 6, height: 6, borderRadius: '50%', background: '#22c55e', animation: 'pulse 1.5s infinite' }} />
                                    LIVE · {formatDuration(sessionDuration)}
                                </div>
                            </>
                        )}
                    </div>
                </div>

                {/* Speech text */}
                <div style={{ textAlign: 'center', maxWidth: 500, padding: '4px 16px', flexShrink: 0 }}>
                    <p style={{
                        fontSize: 22, fontWeight: 500, color: '#1e293b',
                        lineHeight: 1.5, margin: 0,
                    }}>
                        {sessionState === 'waiting'  ? "Ready when you are! Press 'Start Session' to begin. 🌟"
                       : sessionState === 'starting' ? "Starting up… please wait a moment. ⏳"
                       : sessionState === 'ended'    ? (speechText || "Great work today! See you next time. 👋")
                       : (speechText || (voiceState === 'idle' ? "I'm listening… 👂" : ''))}
                    </p>
                </div>

                {/* Avatar */}
                <div style={{ flexShrink: 0 }}>
                    <LaraAvatar state={sessionState === 'waiting' ? 'idle' : voiceState} />
                </div>

                {/* Listening / Thinking — fixed height */}
                <div style={{ height: 72, position: 'relative', width: 180, flexShrink: 0 }}>
                    <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: voiceState === 'listening' && sessionState === 'active' ? 1 : 0, transition: 'opacity 0.4s' }}>
                        <ListeningIndicator isVisible={voiceState === 'listening'} />
                    </div>
                    <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: voiceState === 'thinking' && sessionState === 'active' ? 1 : 0, transition: 'opacity 0.4s' }}>
                        <ThinkingIndicator isVisible={voiceState === 'thinking'} />
                    </div>
                </div>

                {/* Stats strip */}
                {sessionState === 'active' && (
                    <div style={{
                        display: 'flex', background: 'white', borderRadius: 10, overflow: 'hidden',
                        boxShadow: '0 1px 5px rgba(0,0,0,0.05)', flexShrink: 0,
                    }}>
                        {[
                            { label: 'Turn', value: turnCount },
                            { label: 'Level', value: `${difficulty}/5` },
                            { label: 'Mood', value: mood, cap: true },
                            ...(strategy !== 'neutral' ? [{ label: 'Strategy', value: strategy, blue: true }] : []),
                        ].map((item, i, arr) => (
                            <div key={item.label} style={{
                                padding: '8px 16px', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 2,
                                borderRight: i < arr.length - 1 ? '1px solid #f1f5f9' : 'none',
                            }}>
                                <span style={{ fontSize: 9, color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.07em', fontWeight: 700 }}>{item.label}</span>
                                <span style={{ fontSize: 13, fontWeight: 700, color: item.blue ? '#2563eb' : '#1e293b', textTransform: item.cap ? 'capitalize' : 'none' }}>{item.value}</span>
                            </div>
                        ))}
                    </div>
                )}

                {sessionState === 'active' && (
                    <div style={{ width: '100%', maxWidth: 560, display: 'flex', flexDirection: 'column', gap: 8, flexShrink: 0 }}>
                        {visionAlert && (
                            <div style={{
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 12,
                                background: alertColors.bg, border: `1px solid ${alertColors.border}`,
                                borderRadius: 12, padding: '10px 12px', color: alertColors.text,
                                boxShadow: '0 4px 18px rgba(15,23,42,0.06)',
                            }}>
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 2, minWidth: 0 }}>
                                    <span style={{ fontSize: 10, fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                                        {visionAlert.type === 'absence' ? 'Vision Alert' : 'Attention Alert'}
                                    </span>
                                    <span style={{ fontSize: 12, fontWeight: 600 }}>{visionAlert.message}</span>
                                </div>
                                <button
                                    onClick={() => setVisionAlert(null)}
                                    style={{
                                        border: 'none', background: 'transparent', color: alertColors.text,
                                        cursor: 'pointer', fontSize: 18, lineHeight: 1, padding: 0,
                                    }}
                                    aria-label="Dismiss vision alert"
                                >
                                    ×
                                </button>
                            </div>
                        )}

                        <div style={{
                            display: 'flex', alignItems: 'center', gap: 12, flexWrap: 'wrap',
                            background: 'rgba(255,255,255,0.92)', border: '1px solid #dbeafe',
                            borderRadius: 14, padding: '10px 12px',
                            boxShadow: '0 8px 28px rgba(148,163,184,0.14)',
                        }}>
                            <div style={{
                                display: 'flex', alignItems: 'center', gap: 8,
                                background: attentionColors.bg, borderRadius: 999, padding: '6px 10px',
                            }}>
                                <div style={{ width: 8, height: 8, borderRadius: '50%', background: attentionColors.dot }} />
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                    <span style={{ fontSize: 9, color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em' }}>Attention</span>
                                    <span style={{ fontSize: 12, color: attentionColors.text, fontWeight: 700 }}>
                                        {liveVision.attention}
                                    </span>
                                </div>
                            </div>

                            <div style={{ display: 'flex', flexDirection: 'column', gap: 5, minWidth: 140, flex: 1 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <span style={{ fontSize: 9, color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                                        Engagement
                                    </span>
                                    <span style={{ fontSize: 11, color: '#334155', fontWeight: 700 }}>
                                        {Math.round((liveVision.engagement ?? 0) * 100)}%
                                    </span>
                                </div>
                                <div style={{ height: 7, background: '#e2e8f0', borderRadius: 999, overflow: 'hidden' }}>
                                    <div style={{
                                        width: `${Math.max(0, Math.min(100, (liveVision.engagement ?? 0) * 100))}%`,
                                        height: '100%',
                                        background: 'linear-gradient(90deg, #f59e0b 0%, #22c55e 100%)',
                                        borderRadius: 999,
                                        transition: 'width 0.4s ease',
                                    }} />
                                </div>
                            </div>

                            <div style={{
                                display: 'flex', flexDirection: 'column', gap: 1,
                                minWidth: 78,
                            }}>
                                <span style={{ fontSize: 9, color: '#94a3b8', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                                    Presence
                                </span>
                                <span style={{ fontSize: 12, fontWeight: 700, color: liveVision.presence ? '#166534' : '#64748b' }}>
                                    {liveVision.presence ? 'In frame' : 'No face'}
                                </span>
                            </div>

                            {lastGesture && (
                                <div style={{
                                    background: '#dbeafe', color: '#1d4ed8', border: '1px solid #93c5fd',
                                    borderRadius: 999, padding: '7px 12px',
                                    fontSize: 11, fontWeight: 800, letterSpacing: '0.04em',
                                    textTransform: 'uppercase', animation: 'fadeGesture 2s linear forwards',
                                }}>
                                    {gestureLabel}
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Control buttons */}
                <div style={{ flexShrink: 0 }}>
                    {(sessionState === 'waiting' || sessionState === 'ended') && (
                        <button onClick={handleStartSession} disabled={wsStatus !== 'connected'} style={{
                            background: wsStatus === 'connected' ? '#2563eb' : '#cbd5e1',
                            color: 'white', border: 'none', borderRadius: 14,
                            padding: '13px 40px', fontSize: 15, fontWeight: 700,
                            cursor: wsStatus === 'connected' ? 'pointer' : 'not-allowed',
                            boxShadow: wsStatus === 'connected' ? '0 4px 18px rgba(37,99,235,0.3)' : 'none',
                            display: 'flex', alignItems: 'center', gap: 9,
                        }}>
                            <svg width="15" height="15" viewBox="0 0 24 24" fill="white"><polygon points="5,3 19,12 5,21" /></svg>
                            {sessionState === 'ended' ? 'Start New Session' : 'Start Session'}
                        </button>
                    )}
                    {sessionState === 'starting' && (
                        <div style={{
                            background: '#f0fdf4', border: '1px solid #bbf7d0', borderRadius: 14,
                            padding: '13px 40px', fontSize: 14, fontWeight: 600, color: '#16a34a',
                            display: 'flex', alignItems: 'center', gap: 9,
                        }}>
                            <div style={{ width: 15, height: 15, borderRadius: '50%', border: '2px solid #16a34a', borderTopColor: 'transparent', animation: 'spin 0.8s linear infinite' }} />
                            Starting LaRa…
                        </div>
                    )}
                    {sessionState === 'active' && (
                        <button onClick={handleStopSession} style={{
                            background: '#fee2e2', color: '#dc2626',
                            border: '1px solid #fca5a5', borderRadius: 14,
                            padding: '11px 28px', fontSize: 14, fontWeight: 700,
                            cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 8,
                        }}>
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="#dc2626"><rect x="4" y="4" width="16" height="16" rx="2" /></svg>
                            End Session
                        </button>
                    )}
                </div>
            </div>

            {/* ══ RIGHT PANEL ══ */}
            <div style={{
                width: 320, background: 'white', borderLeft: '1px solid #e2e8f0',
                display: 'flex', flexDirection: 'column', flexShrink: 0,
            }}>
                {/* Header */}
                <div style={{ padding: '18px 18px 12px', borderBottom: '1px solid #f1f5f9', flexShrink: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: 13, color: '#1e293b' }}>Live Transcript</div>
                    <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 1 }}>Session: {sessionUuid?.slice(0, 8) ?? '—'}</div>
                    <div style={{
                        marginTop: 8, display: 'inline-flex', alignItems: 'center', gap: 4,
                        background: sessionState === 'active' ? '#f0fdf4' : '#f8fafc',
                        border: `1px solid ${sessionState === 'active' ? '#bbf7d0' : '#e2e8f0'}`,
                        borderRadius: 5, padding: '2px 8px', fontSize: 9, fontWeight: 700,
                        color: sessionState === 'active' ? '#16a34a' : '#94a3b8',
                        textTransform: 'uppercase', letterSpacing: '0.07em',
                    }}>
                        <div style={{ width: 5, height: 5, borderRadius: '50%', background: sessionState === 'active' ? '#22c55e' : '#cbd5e1', animation: sessionState === 'active' ? 'pulse 1.5s infinite' : 'none' }} />
                        {sessionState === 'active' ? 'Live' : sessionState === 'starting' ? 'Starting…' : sessionState === 'ended' ? 'Ended' : 'Waiting'}
                    </div>
                </div>

                {/* Transcript scroll */}
                <div style={{ flex: 1, overflowY: 'auto', padding: '12px 14px', display: 'flex', flexDirection: 'column', gap: 9 }}>
                    {transcript.length === 0 ? (
                        <div style={{ color: '#cbd5e1', fontSize: 12, textAlign: 'center', marginTop: 40 }}>
                            {sessionState === 'waiting' ? 'Press "Start Session" to begin.' : 'Waiting for first turn…'}
                        </div>
                    ) : transcript.map((entry, i) => (
                        <div key={i} style={{ alignSelf: entry.speaker === 'lara' ? 'flex-start' : 'flex-end', maxWidth: '88%' }}>
                            <div style={{ fontSize: 9, fontWeight: 700, marginBottom: 2, color: entry.speaker === 'lara' ? '#2563eb' : '#10b981', textTransform: 'uppercase', letterSpacing: '0.07em' }}>
                                {entry.speaker === 'lara' ? 'LaRa' : 'Child'}
                            </div>
                            <div style={{
                                background: entry.speaker === 'lara' ? '#eff6ff' : '#f0fdf4',
                                border: `1px solid ${entry.speaker === 'lara' ? '#bfdbfe' : '#bbf7d0'}`,
                                borderRadius: entry.speaker === 'lara' ? '3px 12px 12px 12px' : '12px 3px 12px 12px',
                                padding: '7px 11px', fontSize: 12, color: '#1e293b', lineHeight: 1.5,
                            }}>
                                {entry.text}
                            </div>
                        </div>
                    ))}
                    <div ref={transcriptEndRef} />
                </div>

                {/* Footer */}
                <div style={{ padding: '12px 14px', borderTop: '1px solid #f1f5f9', flexShrink: 0 }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '4px 12px', fontSize: 11, color: '#94a3b8' }}>
                        <div>Child: <strong style={{ color: '#475569' }}>{childId ?? '—'}</strong></div>
                        <div>Turns: <strong style={{ color: '#475569' }}>{turnCount}</strong></div>
                        {sessionState === 'active' && (
                            <>
                                <div>Confidence: <strong style={{ color: '#475569' }}>{Math.round(moodConf * 100)}%</strong></div>
                                <div>Time: <strong style={{ color: '#475569' }}>{formatDuration(sessionDuration)}</strong></div>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* ══ SESSION SUMMARY OVERLAY ══ */}
            {showSummary && summary && (
                <div style={{
                    position: 'fixed', inset: 0, zIndex: 200,
                    background: 'rgba(15,23,42,0.6)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    backdropFilter: 'blur(5px)',
                }}>
                    <div style={{
                        background: 'white', borderRadius: 20, padding: '32px 36px',
                        width: 500, maxWidth: '92vw', maxHeight: '90vh', overflowY: 'auto',
                        boxShadow: '0 24px 64px rgba(0,0,0,0.2)',
                    }}>
                        {/* Title */}
                        <div style={{ textAlign: 'center', marginBottom: 24 }}>
                            <div style={{ fontSize: 36, marginBottom: 6 }}>🎉</div>
                            <div style={{ fontSize: 20, fontWeight: 800, color: '#1e293b' }}>Session Complete</div>
                            <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 3 }}>
                                {sessionUuid?.slice(0, 8) ?? '—'} · {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                            </div>
                        </div>

                        {/* Primary stats */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10, marginBottom: 10 }}>
                            {[
                                { icon: '⏱', label: 'Duration',   value: formatDuration(summary.duration) },
                                { icon: '💬', label: 'Turns',      value: summary.turns },
                                { icon: '📈', label: 'Peak Level', value: `${summary.difficultyReached}/5` },
                            ].map(item => (
                                <div key={item.label} style={{ background: '#f8fafc', borderRadius: 10, padding: '14px 10px', textAlign: 'center', border: '1px solid #f1f5f9' }}>
                                    <div style={{ fontSize: 20, marginBottom: 3 }}>{item.icon}</div>
                                    <div style={{ fontSize: 18, fontWeight: 800, color: '#1e293b' }}>{item.value}</div>
                                    <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</div>
                                </div>
                            ))}
                        </div>

                        {/* Secondary stats */}
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: 10, marginBottom: 18 }}>
                            {[
                                { icon: '🤖', label: 'LaRa Responses', value: summary.laraResponses },
                                { icon: '🧒', label: 'Child Turns',     value: summary.childUtterances },
                                { icon: '✨', label: 'Engagement',      value: `${summary.engagementPct}%` },
                            ].map(item => (
                                <div key={item.label} style={{ background: '#f8fafc', borderRadius: 10, padding: '12px 8px', textAlign: 'center', border: '1px solid #f1f5f9' }}>
                                    <div style={{ fontSize: 17, marginBottom: 2 }}>{item.icon}</div>
                                    <div style={{ fontSize: 16, fontWeight: 700, color: '#1e293b' }}>{item.value}</div>
                                    <div style={{ fontSize: 9, color: '#94a3b8', marginTop: 2, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{item.label}</div>
                                </div>
                            ))}
                        </div>

                        {/* Mood breakdown */}
                        <div style={{ background: '#f8fafc', borderRadius: 12, padding: '14px 16px', marginBottom: 20, border: '1px solid #f1f5f9' }}>
                            <div style={{ fontSize: 10, fontWeight: 700, color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.07em', marginBottom: 10 }}>Mood Profile</div>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 7, flexWrap: 'wrap' }}>
                                {Object.entries(summary.moodBreakdown).sort((a, b) => b[1] - a[1]).map(([m, count]) => {
                                    const mc2 = moodColor(m);
                                    const total = Object.values(summary.moodBreakdown).reduce((a, b) => a + b, 0);
                                    const pct = Math.round((count / total) * 100);
                                    return (
                                        <div key={m} style={{
                                            display: 'flex', alignItems: 'center', gap: 4,
                                            background: mc2.bg, border: `1px solid ${mc2.dot}44`,
                                            borderRadius: 20, padding: '4px 10px',
                                            fontSize: 11, fontWeight: 600, color: mc2.text, textTransform: 'capitalize',
                                        }}>
                                            <div style={{ width: 5, height: 5, borderRadius: '50%', background: mc2.dot }} />
                                            {m} · {pct}%
                                        </div>
                                    );
                                })}
                                {Object.keys(summary.moodBreakdown).length === 0 && (
                                    <div style={{ fontSize: 12, color: '#94a3b8' }}>No mood data recorded this session</div>
                                )}
                            </div>
                        </div>

                        {/* Actions */}
                        <div style={{ display: 'flex', gap: 10 }}>
                            <button onClick={() => { setShowSummary(false); handleStartSession(); }} disabled={wsStatus !== 'connected'} style={{
                                flex: 1, background: '#2563eb', color: 'white',
                                border: 'none', borderRadius: 11, padding: '12px',
                                fontSize: 13, fontWeight: 700, cursor: 'pointer',
                                display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7,
                            }}>
                                <svg width="12" height="12" viewBox="0 0 24 24" fill="white"><polygon points="5,3 19,12 5,21" /></svg>
                                New Session
                            </button>
                            <button onClick={() => navigate(`/dashboard/family/${childId}`)} style={{
                                flex: 1, background: '#f1f5f9', color: '#475569',
                                border: '1px solid #e2e8f0', borderRadius: 11, padding: '12px',
                                fontSize: 13, fontWeight: 700, cursor: 'pointer',
                            }}>
                                Back to Dashboard
                            </button>
                        </div>
                    </div>
                </div>
            )}

            <style>{`
                @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.35; } }
                @keyframes spin  { to { transform: rotate(360deg); } }
                @keyframes fadeGesture { 0% { opacity: 0; transform: translateY(4px); } 15% { opacity: 1; transform: translateY(0); } 100% { opacity: 0; transform: translateY(-2px); } }
            `}</style>
        </div>
    );
};

export default VoiceSessionPage;
