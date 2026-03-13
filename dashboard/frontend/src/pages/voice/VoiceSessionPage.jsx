/**
 * VoiceSessionPage — Live WebSocket-connected session UI
 * 
 * Connects to the LaRa Python pipeline via WebSocket on ws://localhost:8765.
 * Receives JSON events and maps them to the avatar/bubble/indicator state.
 *
 * State machine (driven by server events, not setTimeout):
 *   idle → listening → thinking → speaking → listening → ...
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams } from 'react-router-dom';
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

    // ── Core voice state (driven by WebSocket events) ──────────────
    const [voiceState, setVoiceState]       = useState('idle');
    const [speechText, setSpeechText]       = useState('');
    const [transcript, setTranscript]       = useState([]);  // [{speaker, text, timestamp}]

    // ── Session metadata (from server events) ──────────────────────
    const [turnCount, setTurnCount]         = useState(0);
    const [difficulty, setDifficulty]       = useState(2);
    const [mood, setMood]                   = useState('neutral');
    const [moodConf, setMoodConf]           = useState(0.0);
    const [strategy, setStrategy]           = useState('neutral');

    // ── Connection state ───────────────────────────────────────────
    const [wsStatus, setWsStatus]           = useState('connecting');
    const [reconnectCount, setReconnectCount] = useState(0);

    // ── Refs ───────────────────────────────────────────────────────
    const wsRef               = useRef(null);
    const reconnectTimeoutRef = useRef(null);
    const reconnectCountRef   = useRef(0);
    const transcriptEndRef    = useRef(null);

    // ── Auto-scroll transcript ──────────────────────────────────────
    useEffect(() => {
        transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [transcript]);

    // ── WebSocket event handler ──────────────────────────────────────
    const handleMessage = useCallback((event) => {
        let msg;
        try {
            msg = JSON.parse(event.data);
        } catch {
            return;
        }

        switch (msg.type) {

            case 'system_state':
                setVoiceState(msg.mode === 'resting' ? 'idle' : msg.mode);
                setTurnCount(msg.turn_count ?? 0);
                setDifficulty(msg.difficulty ?? 2);
                if (msg.mode === 'listening' || msg.mode === 'thinking' || msg.mode === 'resting') {
                    setTimeout(() => {
                        if (msg.mode !== 'speaking') setSpeechText('');
                    }, 1500);
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

            case 'lara_chunk':
                // Streaming chunk — uncomment for typewriter effect:
                // setSpeechText(prev => prev + msg.chunk);
                break;

            case 'mood_update':
                setMood(msg.mood);
                setMoodConf(msg.confidence);
                break;

            case 'difficulty_change':
                setDifficulty(msg.new_difficulty);
                break;

            case 'session_ended':
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

    // ── WebSocket connection lifecycle ──────────────────────────────
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

        ws.onerror = () => {
            ws.close();
        };
    }, [handleMessage]);

    useEffect(() => {
        connect();
        return () => {
            clearTimeout(reconnectTimeoutRef.current);
            wsRef.current?.close();
        };
    }, [connect]);

    // ── Connection status badge ──────────────────────────────────────
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

    // ── Render ───────────────────────────────────────────────────────
    return (
        <div className="fixed inset-0 min-h-screen w-full flex" style={{ background: '#eef4ff', fontFamily: 'Arial, sans-serif' }}>

            {/* ── Left panel: Avatar + bubble (child-facing) ── */}
            <div className="flex flex-col items-center justify-between flex-1" style={{ padding: '32px 24px' }}>

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
                        text={speechText || (voiceState === 'idle' ? "Hello! Say 'friday' to wake me up. 👋" : '')}
                        isVisible={voiceState === 'speaking' || voiceState === 'idle'}
                    />
                </div>

                {/* LaRa Avatar — central element */}
                <div style={{ flexShrink: 0, padding: '16px 0' }}>
                    <LaraAvatar state={voiceState} />
                </div>

                {/* Listening / Thinking indicators */}
                <div style={{ flex: 1, display: 'flex', alignItems: 'flex-start', paddingTop: 24, position: 'relative', minHeight: 80 }}>
                    <div style={{ position: 'absolute', opacity: voiceState === 'listening' ? 1 : 0, transition: 'opacity 0.4s' }}>
                        <ListeningIndicator isVisible={voiceState === 'listening'} />
                    </div>
                    <div style={{ position: 'absolute', opacity: voiceState === 'thinking' ? 1 : 0, transition: 'opacity 0.4s' }}>
                        <ThinkingIndicator isVisible={voiceState === 'thinking'} />
                    </div>
                </div>

                {/* Session metadata strip */}
                <div style={{
                    display: 'flex', gap: 16, padding: '10px 20px',
                    background: 'white', borderRadius: 12,
                    boxShadow: '0 1px 4px rgba(0,0,0,0.06)', fontSize: 13, color: '#64748b',
                }}>
                    <span>Turn <strong>{turnCount}</strong></span>
                    <span>|</span>
                    <span>Level <strong>{difficulty}</strong></span>
                    <span>|</span>
                    <span>Mood <strong style={{ textTransform: 'capitalize' }}>{mood}</strong></span>
                    {strategy !== 'neutral' && <>
                        <span>|</span>
                        <span>Strategy <strong style={{ color: '#2563eb' }}>{strategy}</strong></span>
                    </>}
                </div>
            </div>

            {/* ── Right panel: Live transcript (caregiver-facing) ── */}
            <div style={{
                width: 320, background: 'white', borderLeft: '1px solid #e2e8f0',
                display: 'flex', flexDirection: 'column', padding: '24px 0',
            }}>
                <div style={{ padding: '0 20px 16px', borderBottom: '1px solid #f1f5f9' }}>
                    <div style={{ fontWeight: 700, fontSize: 15, color: '#1e293b' }}>Live Transcript</div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginTop: 2 }}>Session: {sessionUuid?.slice(0, 8) ?? '—'}</div>
                </div>

                <div style={{ flex: 1, overflowY: 'auto', padding: '16px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
                    {transcript.length === 0 && (
                        <div style={{ color: '#94a3b8', fontSize: 13, textAlign: 'center', marginTop: 32 }}>
                            Waiting for session to begin…
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
                    <div style={{ marginTop: 4 }}>
                        Mood confidence: {Math.round(moodConf * 100)}%
                    </div>
                </div>
            </div>

        </div>
    );
};

export default VoiceSessionPage;
