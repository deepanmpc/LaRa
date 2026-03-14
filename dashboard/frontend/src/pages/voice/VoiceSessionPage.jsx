/**
 * VoiceSessionPage — Live WebSocket-connected session UI
 *
 * Key changes vs. original:
 *  - Pipeline is NOT triggered automatically on page load.
 *  - A "Start Session" button sends {"type":"session_start"} over WS.
 *  - A "Stop Session" button sends {"type":"session_stop"} over WS.
 *  - Pipeline state is driven by server acks (session_ack) and events.
 *  - UI shows a clear "waiting to start" state before session begins.
 *
 * State machine:
 *   idle (waiting) → [Start Session clicked] → starting → listening
 *     → thinking → speaking → listening → ... → idle
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import LaraAvatar from '../../components/voice/LaraAvatar';
import SpeechBubble from '../../components/voice/SpeechBubble';
import ListeningIndicator from '../../components/voice/ListeningIndicator';
import ThinkingIndicator from '../../components/voice/ThinkingIndicator';

// WebSocket endpoint — must match ws_server.py WS_PORT
const WS_URL = 'ws://localhost:8765';

// Reconnect config
const RECONNECT_DELAY_MS = 2000;
const MAX_RECONNECT_ATTEMPTS = 10;

const VoiceSessionPage = () => {
    const { childId, sessionUuid } = useParams();
    const navigate = useNavigate();

    // ── Core voice state (driven by WebSocket events) ──────────────
    const [voiceState, setVoiceState]       = useState('idle');
    const [speechText, setSpeechText]       = useState('');
    const [transcript, setTranscript]       = useState([]);

    // ── Session gate state ─────────────────────────────────────────
    // 'waiting'  — connected, not started
    // 'starting' — sent session_start, awaiting ack
    // 'active'   — pipeline running
    // 'ended'    — session finished
    const [sessionState, setSessionState]   = useState('waiting');

    // ── Session metadata (from server events) ──────────────────────
    const [turnCount, setTurnCount]         = useState(0);
    const [difficulty, setDifficulty]       = useState(2);
    const [mood, setMood]                   = useState('neutral');
    const [moodConf, setMoodConf]           = useState(0.0);
    const [strategy, setStrategy]           = useState('neutral');
    const [sessionDuration, setSessionDuration] = useState(0);

    // ── Connection state ───────────────────────────────────────────
    const [wsStatus, setWsStatus]           = useState('connecting');
    const [reconnectCount, setReconnectCount] = useState(0);

    // ── Refs ───────────────────────────────────────────────────────
    const wsRef               = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const reconnectCountRef   = useRef(0);
    const transcriptEndRef    = useRef(null);
    const sessionStartTimeRef = useRef(null);
    const durationTimerRef    = useRef(null);

    // ── Auto-scroll transcript ──────────────────────────────────────
    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [transcript]);

    // ── Session duration timer ──────────────────────────────────────
    useEffect(() => {
        if (sessionState === 'active') {
            sessionStartTimeRef.current = Date.now();
            durationTimerRef.current = setInterval(() => {
                setSessionDuration(Math.floor((Date.now() - sessionStartTimeRef.current) / 1000));
            }, 1000);
        } else {
            clearInterval(durationTimerRef.current);
        }
        return () => clearInterval(durationTimerRef.current);
    }, [sessionState]);

    // ── Format duration ────────────────────────────────────────────
    const formatDuration = (secs) => {
        const m = Math.floor(secs / 60).toString().padStart(2, '0');
        const s = (secs % 60).toString().padStart(2, '0');
        return `${m}:${s}`;
    };

    // ── WebSocket event handler ────────────────────────────────────
    const handleMessage = useCallback((event) => {
        let msg;
        try { msg = JSON.parse(event.data); }
        catch { return; }

        switch (msg.type) {

            case 'system_state':
                setVoiceState(msg.mode === 'resting' ? 'idle' : msg.mode);
                setTurnCount(msg.turn_count ?? 0);
                setDifficulty(msg.difficulty ?? 2);
                if (msg.mode !== 'speaking') {
                    setTimeout(() => setSpeechText(''), 1500);
                }
                break;

            case 'session_ack':
                if (msg.status === 'starting') {
                    setSessionState('active');
                } else if (msg.status === 'stopping') {
                    setSessionState('ended');
                    setVoiceState('idle');
                } else if (msg.status === 'already_running') {
                    setSessionState('active');
                } else if (msg.status === 'not_running') {
                    setSessionState('waiting');
                }
                break;

            case 'transcript':
                setTranscript(prev => [...prev, {
                    speaker: msg.speaker,
                    text: msg.text,
                    timestamp: msg.timestamp,
                }]);
                break;

            case 'lara_response':
                setSpeechText(msg.text);
                setMood(msg.mood ?? 'neutral');
                setMoodConf(msg.mood_confidence ?? 0.0);
                setStrategy(msg.strategy ?? 'neutral');
                setTranscript(prev => [...prev, {
                    speaker: 'lara',
                    text: msg.text,
                    timestamp: Date.now() / 1000,
                }]);
                break;

            case 'mood_update':
                setMood(msg.mood);
                setMoodConf(msg.confidence);
                break;

            case 'difficulty_change':
                setDifficulty(msg.new_difficulty);
                break;

            case 'session_ended':
                setSessionState('ended');
                setVoiceState('idle');
                setSpeechText('Session ended. Goodbye! 👋');
                break;

            case 'error':
                console.error('[LaRa Bridge] Pipeline error:', msg.message);
                break;

            default:
                break;
        }
    }, []);

    // ── WebSocket connection lifecycle ─────────────────────────────
    const connect = useCallback(() => {
        if (reconnectCountRef.current >= MAX_RECONNECT_ATTEMPTS) {
            setWsStatus('error');
            return;
        }

        setWsStatus('connecting');
        const ws = new WebSocket(WS_URL);
        wsRef.current = ws;

        ws.onopen = () => {
            setWsStatus('connected');
            reconnectCountRef.current = 0;
            setReconnectCount(0);
        };

        ws.onmessage = handleMessage;

        ws.onclose = () => {
            setWsStatus('disconnected');
            reconnectCountRef.current += 1;
            setReconnectCount(reconnectCountRef.current);
            if (reconnectCountRef.current < MAX_RECONNECT_ATTEMPTS) {
                reconnectTimeoutRef.current = setTimeout(connect, RECONNECT_DELAY_MS);
            } else {
                setWsStatus('error');
            }
        };

        ws.onerror = () => { ws.close(); };
    }, [handleMessage]);

    useEffect(() => {
        connect();
        return () => {
            clearTimeout(reconnectTimeoutRef.current);
            wsRef.current?.close();
        };
    }, [connect]);

    // ── Session control ────────────────────────────────────────────
    const sendCommand = (type) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type }));
        }
    };

    const handleStartSession = () => {
        if (wsStatus !== 'connected') return;
        setSessionState('starting');
        setTranscript([]);
        setSpeechText('');
        sendCommand('session_start');
    };

    const handleStopSession = () => {
        sendCommand('session_stop');
        setSessionState('ended');
        setVoiceState('idle');
    };

    // ── Connection status config ───────────────────────────────────
    const statusColors = {
        connecting:   '#f59e0b',
        connected:    '#10b981',
        disconnected: '#ef4444',
        error:        '#ef4444',
    };
    const statusLabels = {
        connecting:   'Connecting to LaRa…',
        connected:    'Connected',
        disconnected: `Reconnecting… (${reconnectCount}/${MAX_RECONNECT_ATTEMPTS})`,
        error:        'Cannot reach LaRa. Is main.py running?',
    };

    // ── Session gate overlay ───────────────────────────────────────
    const showGate = sessionState === 'waiting' || sessionState === 'starting';

    // ── Render ─────────────────────────────────────────────────────
    return (
        <div className="fixed inset-0 min-h-screen w-full flex" style={{ background: '#eef4ff', fontFamily: 'Arial, sans-serif' }}>

            {/* ── Left panel: Avatar + bubble (child-facing) ── */}
            <div className="flex flex-col items-center justify-between flex-1" style={{ padding: '32px 24px', position: 'relative' }}>

                {/* Connection status badge */}
                <div style={{
                    display: 'flex', alignItems: 'center', gap: 8,
                    background: 'white', borderRadius: 20, padding: '6px 16px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.08)', fontSize: 13,
                    color: statusColors[wsStatus], fontWeight: 600,
                }}>
                    <div style={{
                        width: 8, height: 8, borderRadius: '50%',
                        background: statusColors[wsStatus],
                        animation: wsStatus === 'connected' ? 'pulse 2s infinite' : 'none',
                    }} />
                    {statusLabels[wsStatus]}
                </div>

                {/* Speech bubble — LaRa's text */}
                <div style={{ flex: 1, display: 'flex', alignItems: 'flex-end', paddingBottom: 24, width: '100%', maxWidth: 480 }}>
                    <SpeechBubble
                        text={
                            sessionState === 'waiting'
                                ? "Ready when you are! Press 'Start Session' to begin. 🌟"
                                : sessionState === 'starting'
                                    ? "Starting up… please wait a moment. ⏳"
                                    : sessionState === 'ended'
                                        ? (speechText || "Great work today! See you next time. 👋")
                                        : (speechText || (voiceState === 'idle' ? "I'm listening… 👂" : ''))
                        }
                        isVisible={true}
                    />
                </div>

                {/* LaRa Avatar — central element */}
                <div style={{ flexShrink: 0, padding: '16px 0' }}>
                    <LaraAvatar state={sessionState === 'waiting' ? 'idle' : voiceState} />
                </div>

                {/* Listening / Thinking indicators */}
                <div style={{ flex: 1, display: 'flex', alignItems: 'flex-start', paddingTop: 24, position: 'relative', minHeight: 80 }}>
                    <div style={{ position: 'absolute', opacity: voiceState === 'listening' && sessionState === 'active' ? 1 : 0, transition: 'opacity 0.4s' }}>
                        <ListeningIndicator isVisible={voiceState === 'listening'} />
                    </div>
                    <div style={{ position: 'absolute', opacity: voiceState === 'thinking' && sessionState === 'active' ? 1 : 0, transition: 'opacity 0.4s' }}>
                        <ThinkingIndicator isVisible={voiceState === 'thinking'} />
                    </div>
                </div>

                {/* ── Session control button ── */}
                <div style={{ display: 'flex', gap: 12, alignItems: 'center', paddingTop: 8 }}>
                    {(sessionState === 'waiting' || sessionState === 'ended') && (
                        <button
                            onClick={handleStartSession}
                            disabled={wsStatus !== 'connected'}
                            style={{
                                background: wsStatus === 'connected' ? '#2563eb' : '#94a3b8',
                                color: 'white',
                                border: 'none',
                                borderRadius: 14,
                                padding: '14px 36px',
                                fontSize: 16,
                                fontWeight: 700,
                                cursor: wsStatus === 'connected' ? 'pointer' : 'not-allowed',
                                boxShadow: wsStatus === 'connected' ? '0 4px 16px rgba(37,99,235,0.35)' : 'none',
                                transition: 'all 0.2s',
                                display: 'flex', alignItems: 'center', gap: 10,
                            }}
                        >
                            {/* Play icon */}
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="white">
                                <polygon points="5,3 19,12 5,21" />
                            </svg>
                            {sessionState === 'ended' ? 'Start New Session' : 'Start Session'}
                        </button>
                    )}

                    {sessionState === 'starting' && (
                        <div style={{
                            background: '#f0fdf4', border: '1px solid #bbf7d0',
                            borderRadius: 14, padding: '14px 36px',
                            fontSize: 15, fontWeight: 600, color: '#16a34a',
                            display: 'flex', alignItems: 'center', gap: 10,
                        }}>
                            <div style={{
                                width: 16, height: 16, borderRadius: '50%',
                                border: '2px solid #16a34a', borderTopColor: 'transparent',
                                animation: 'spin 0.8s linear infinite',
                            }} />
                            Starting LaRa…
                        </div>
                    )}

                    {sessionState === 'active' && (
                        <>
                            {/* Live indicator */}
                            <div style={{
                                display: 'flex', alignItems: 'center', gap: 8,
                                background: '#f0fdf4', border: '1px solid #bbf7d0',
                                borderRadius: 20, padding: '8px 18px', fontSize: 13,
                                color: '#16a34a', fontWeight: 600,
                            }}>
                                <div style={{
                                    width: 8, height: 8, borderRadius: '50%',
                                    background: '#22c55e', animation: 'pulse 1.5s infinite',
                                }} />
                                LIVE · {formatDuration(sessionDuration)}
                            </div>

                            <button
                                onClick={handleStopSession}
                                style={{
                                    background: '#fee2e2', color: '#dc2626',
                                    border: '1px solid #fca5a5', borderRadius: 14,
                                    padding: '10px 24px', fontSize: 14,
                                    fontWeight: 600, cursor: 'pointer',
                                    display: 'flex', alignItems: 'center', gap: 8,
                                    transition: 'all 0.2s',
                                }}
                            >
                                {/* Stop icon */}
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="#dc2626">
                                    <rect x="4" y="4" width="16" height="16" rx="2" />
                                </svg>
                                End Session
                            </button>
                        </>
                    )}
                </div>

                {/* Session metadata strip */}
                {sessionState === 'active' && (
                    <div style={{
                        display: 'flex', gap: 16, padding: '10px 20px', marginTop: 8,
                        background: 'white', borderRadius: 12,
                        boxShadow: '0 1px 4px rgba(0,0,0,0.06)', fontSize: 13, color: '#64748b',
                    }}>
                        <span>Turn <strong>{turnCount}</strong></span>
                        <span>|</span>
                        <span>Level <strong>{difficulty}</strong></span>
                        <span>|</span>
                        <span>Mood <strong style={{ textTransform: 'capitalize' }}>{mood}</strong></span>
                        {strategy !== 'neutral' && (
                            <>
                                <span>|</span>
                                <span>Strategy <strong style={{ color: '#2563eb' }}>{strategy}</strong></span>
                            </>
                        )}
                    </div>
                )}
            </div>

            {/* ── Right panel: Live transcript (caregiver-facing) ── */}
            <div style={{
                width: 320, background: 'white', borderLeft: '1px solid #e2e8f0',
                display: 'flex', flexDirection: 'column', padding: '24px 0',
            }}>
                <div style={{ padding: '0 20px 16px', borderBottom: '1px solid #f1f5f9' }}>
                    <div style={{ fontWeight: 700, fontSize: 15, color: '#1e293b' }}>Live Transcript</div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>
                        Session: {sessionUuid?.slice(0, 8) ?? '—'}
                    </div>

                    {/* Session state badge */}
                    <div style={{
                        marginTop: 10, display: 'inline-flex', alignItems: 'center', gap: 6,
                        background: sessionState === 'active' ? '#f0fdf4' : '#f8fafc',
                        border: `1px solid ${sessionState === 'active' ? '#bbf7d0' : '#e2e8f0'}`,
                        borderRadius: 8, padding: '4px 10px', fontSize: 11, fontWeight: 600,
                        color: sessionState === 'active' ? '#16a34a' : '#94a3b8',
                        textTransform: 'uppercase', letterSpacing: '0.05em',
                    }}>
                        <div style={{
                            width: 6, height: 6, borderRadius: '50%',
                            background: sessionState === 'active' ? '#22c55e' : '#cbd5e1',
                            animation: sessionState === 'active' ? 'pulse 1.5s infinite' : 'none',
                        }} />
                        {sessionState === 'active' ? 'Session Active' :
                         sessionState === 'starting' ? 'Starting…' :
                         sessionState === 'ended' ? 'Session Ended' : 'Waiting to Start'}
                    </div>
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {transcript.length === 0 && (
                        <div style={{ color: '#94a3b8', fontSize: 13, textAlign: 'center', marginTop: 32 }}>
                            {sessionState === 'waiting'
                                ? 'Press "Start Session" to begin.'
                                : 'Waiting for session to begin…'}
                        </div>
                    )}
                    {transcript.map((entry, i) => (
                        <div key={i} style={{
                            alignSelf: entry.speaker === 'lara' ? 'flex-start' : 'flex-end',
                            maxWidth: '85%',
                        }}>
                            <div style={{
                                fontSize: 11, fontWeight: 600, marginBottom: 3,
                                color: entry.speaker === 'lara' ? '#2563eb' : '#10b981',
                                textTransform: 'uppercase', letterSpacing: '0.05em',
                            }}>
                                {entry.speaker === 'lara' ? 'LaRa' : 'Child'}
                            </div>
                            <div style={{
                                background: entry.speaker === 'lara' ? '#eff6ff' : '#f0fdf4',
                                border: `1px solid ${entry.speaker === 'lara' ? '#bfdbfe' : '#bbf7d0'}`,
                                borderRadius: entry.speaker === 'lara' ? '4px 16px 16px 16px' : '16px 4px 16px 16px',
                                padding: '10px 14px', fontSize: 14, color: '#1e293b', lineHeight: 1.5,
                            }}>
                                {entry.text}
                            </div>
                        </div>
                    ))}
                    <div ref={transcriptEndRef} />
                </div>

                {/* Caregiver info footer */}
                <div style={{ padding: '16px 20px', borderTop: '1px solid #f1f5f9', fontSize: 12, color: '#94a3b8' }}>
                    <div>Child ID: {childId ?? '—'}</div>
                    {sessionState === 'active' && (
                        <div style={{ marginTop: 4 }}>
                            Mood confidence: {Math.round(moodConf * 100)}%
                        </div>
                    )}
                    {sessionState === 'active' && (
                        <div style={{ marginTop: 4 }}>
                            Duration: {formatDuration(sessionDuration)}
                        </div>
                    )}
                </div>
            </div>

            {/* CSS animations */}
            <style>{`
                @keyframes pulse {
                    0%, 100% { opacity: 1; }
                    50% { opacity: 0.4; }
                }
                @keyframes spin {
                    to { transform: rotate(360deg); }
                }
            `}</style>
        </div>
    );
};

export default VoiceSessionPage;