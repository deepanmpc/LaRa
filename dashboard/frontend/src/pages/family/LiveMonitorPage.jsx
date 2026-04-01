import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';

const WS_URL = 'ws://localhost:8765';
const VISION_URL = 'http://localhost:8001/latest';
const RECONNECT_DELAY_MS = 2000;
const MAX_RECONNECT_ATTEMPTS = 10;

const STRATEGY_MAP = {
  neutral: "Standard pacing",
  frustrated: "Simplified, slower — reassurance active",
  happy: "Gentle energy match",
  anxious: "Grounding mode — slow and predictable",
  sad: "Comfort mode — reduced task load",
  quiet: "Low pressure — gentle re-engagement",
};

const MOOD_COLORS = {
  happy: 'var(--color-accent)',
  frustrated: '#f97316',
  anxious: '#c084fc',
  sad: '#60a5fa',
  neutral: 'var(--color-text-secondary)',
  quiet: 'var(--color-text-secondary)',
};

const ATTENTION_COLORS = {
  FOCUSED: 'var(--color-accent)',
  DISTRACTED: '#f59e0b',
  ABSENT: 'var(--color-danger)',
  UNKNOWN: 'var(--color-text-muted)',
};

const LiveMonitorPage = () => {
  const { childId, sessionUuid } = useParams();
  const navigate = useNavigate();

  // WS state
  const [wsStatus, setWsStatus] = useState('connecting');
  const [sessionState, setSessionState] = useState({ mode: 'unknown', turn_count: 0, difficulty: 2 });
  const [mood, setMood] = useState({ mood: 'neutral', confidence: 0, regulation: {} });
  const [strategy, setStrategy] = useState('neutral');
  const [transcript, setTranscript] = useState([]);
  const [events, setEvents] = useState([]);
  const [moodHistory, setMoodHistory] = useState([]);
  const [reconnectCount, setReconnectCount] = useState(0);

  // Vision state
  const [vision, setVision] = useState(null);
  const [visionStatus, setVisionStatus] = useState('polling');

  // Child profile
  const [childProfile, setChildProfile] = useState(null);

  // Session
  const [sessionEnded, setSessionEnded] = useState(false);
  const [elapsed, setElapsed] = useState(0);

  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectCountRef = useRef(0);
  const transcriptEndRef = useRef(null);
  const startTimeRef = useRef(Date.now());

  const formatDuration = (secs) => {
    const m = Math.floor(secs / 60).toString().padStart(2, '0');
    const s = (secs % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  useEffect(() => {
    transcriptEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [transcript]);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get(`/family/dashboard/${childId}`);
        setChildProfile(response.data.childProfile);
      } catch (err) {
        console.error('Failed to fetch child profile', err);
      }
    };
    fetchProfile();
  }, [childId]);

  useEffect(() => {
    if (sessionEnded) return;
    const timer = setInterval(() => {
      setElapsed(Math.floor((Date.now() - startTimeRef.current) / 1000));
    }, 1000);
    return () => clearInterval(timer);
  }, [sessionEnded]);

  const addEvent = useCallback((text) => {
    setEvents(prev => [{ text, timestamp: Date.now() / 1000 }, ...prev].slice(0, 30));
  }, []);

  const handleMessage = useCallback((event) => {
    let msg;
    try { msg = JSON.parse(event.data); } catch { return; }

    switch (msg.type) {
      case 'system_state':
        setSessionState(prev => ({
          ...prev,
          mode: msg.mode,
          turn_count: msg.turn_count ?? prev.turn_count,
          difficulty: msg.difficulty ?? prev.difficulty
        }));
        break;

      case 'lara_response':
        setStrategy(msg.strategy ?? 'neutral');
        setMood(prev => ({
          ...prev,
          mood: msg.mood ?? prev.mood,
          confidence: msg.mood_confidence ?? prev.confidence
          // Keep regulation as is
        }));
        setMoodHistory(prev => [...prev, msg.mood ?? 'neutral'].slice(-10));
        setTranscript(prev => [...prev, { speaker: 'lara', text: msg.text, timestamp: Date.now() / 1000 }].slice(-50));
        if (msg.mood) addEvent(`Mood: ${msg.mood} (conf: ${(msg.mood_confidence * 100).toFixed(0)}%)`);
        if (msg.strategy && msg.strategy !== 'neutral') {
          addEvent(`Strategy \u2192 ${msg.strategy}`);
        }
        break;

      case 'mood_update':
        setMood(prev => ({
          ...prev,
          mood: msg.mood ?? prev.mood,
          confidence: msg.confidence ?? prev.confidence,
          regulation: msg.regulation ?? prev.regulation
        }));
        setMoodHistory(prev => [...prev, msg.mood ?? 'neutral'].slice(-10));
        addEvent(`Mood updated: ${msg.mood} (conf: ${(msg.confidence * 100).toFixed(0)}%)`);
        break;

      case 'transcript':
        setTranscript(prev => [...prev, { speaker: msg.speaker, text: msg.text, timestamp: msg.timestamp }].slice(-50));
        break;

      case 'difficulty_change':
        setSessionState(prev => ({ ...prev, difficulty: msg.new_difficulty }));
        addEvent(`${msg.direction === 'up' ? '\u2191' : '\u2193'} Difficulty increased to ${msg.new_difficulty}`);
        break;

      case 'session_ended':
        setSessionEnded(true);
        addEvent(`Session ended: ${msg.reason ?? 'natural end'}`);
        break;

      default: break;
    }
  }, [addEvent]);

  const connect = useCallback(function connectSocket() {
    if (reconnectCountRef.current >= MAX_RECONNECT_ATTEMPTS) { setWsStatus('error'); return; }
    if (wsRef.current) {
      wsRef.current.onclose = null;
      wsRef.current.onerror = null;
      wsRef.current.onmessage = null;
      wsRef.current.close();
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
      if (sessionEnded) return;
      setWsStatus('disconnected');
      reconnectCountRef.current += 1;
      setReconnectCount(reconnectCountRef.current);
      if (reconnectCountRef.current < MAX_RECONNECT_ATTEMPTS)
        reconnectTimeoutRef.current = setTimeout(connectSocket, RECONNECT_DELAY_MS);
      else setWsStatus('error');
    };
    ws.onerror = () => ws.close();
  }, [handleMessage, sessionEnded]);

  useEffect(() => {
    connect();
    return () => {
      clearTimeout(reconnectTimeoutRef.current);
      if (wsRef.current) {
        wsRef.current.onclose = null;
        wsRef.current.onerror = null;
        wsRef.current.onmessage = null;
        wsRef.current.close();
      }
    };
  }, [connect]);

  useEffect(() => {
    if (sessionEnded) return;
    const interval = setInterval(async () => {
      try {
        const r = await fetch(VISION_URL);
        if (r.ok) {
          const data = await r.json();
          setVision(data);
          setVisionStatus('online');
        } else {
          setVisionStatus('error');
        }
      } catch {
        setVisionStatus('offline');
      }
    }, 500);
    return () => clearInterval(interval);
  }, [sessionEnded]);

  const Gauge = ({ label, value, color = 'var(--color-primary)' }) => (
    <div style={{ marginBottom: 12 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: 11, fontWeight: 600, color: 'var(--color-text-secondary)' }}>
        <span>{label}</span>
        <span style={{ transition: 'opacity 0.4s ease' }}>{(value * 100).toFixed(0)}%</span>
      </div>
      <div style={{ height: 6, background: 'var(--color-border)', borderRadius: 3, overflow: 'hidden' }}>
        <div style={{
          width: `${Math.max(0, Math.min(100, value * 100))}%`,
          height: '100%',
          background: color,
          transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
        }} />
      </div>
    </div>
  );

  const MetricChip = ({ label, value }) => (
    <div style={{ background: 'var(--color-bg)', padding: '8px', borderRadius: 6, border: '1px solid var(--color-border)', transition: 'all 0.4s ease' }}>
      <div style={{ fontSize: 9, color: 'var(--color-text-muted)', fontWeight: 700, textTransform: 'uppercase', marginBottom: 2 }}>{label}</div>
      <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--color-text-primary)', transition: 'color 0.4s ease' }}>{(value * 100).toFixed(0)}%</div>
    </div>
  );

  const StatusChip = ({ label, active }) => (
    <div style={{
      fontSize: 10, fontWeight: 700, padding: '4px 8px', borderRadius: 4,
      background: active ? 'var(--color-danger)' : 'var(--color-bg)',
      color: active ? '#ffffff' : 'var(--color-text-muted)',
      border: active ? '1px solid var(--color-danger)' : '1px solid var(--color-border)',
      textTransform: 'uppercase',
      transition: 'all 0.4s ease'
    }}>
      {label}
    </div>
  );

  if (!childProfile) {
    return (
      <div style={{ background: 'var(--color-bg)', height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--color-text-secondary)' }}>
        Loading child profile...
      </div>
    );
  }

  return (
    <div style={{
      background: 'var(--color-bg)', color: 'var(--color-text-primary)', minHeight: '100vh',
      fontFamily: "'Inter', sans-serif", display: 'flex', flexDirection: 'column'
    }}>
      {/* Header */}
      <header style={{
        height: '64px', background: 'var(--color-surface)', borderBottom: '1px solid var(--color-border)',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '0 24px', position: 'sticky', top: 0, zIndex: 100
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ fontSize: 20, fontWeight: 900, color: 'var(--color-primary)', letterSpacing: '-0.02em' }}>LaRa</div>
          <div style={{ height: 24, width: 1, background: 'var(--color-border)' }} />
          <div style={{ fontSize: 16, fontWeight: 700, color: 'var(--color-text-primary)' }}>Live Session Monitor</div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 32 }}>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 10, color: 'var(--color-text-muted)', fontWeight: 800, textTransform: 'uppercase', marginBottom: 2 }}>Patient</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-text-primary)' }}>{childProfile.name}</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 10, color: 'var(--color-text-muted)', fontWeight: 800, textTransform: 'uppercase', marginBottom: 2 }}>Session ID</div>
            <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--color-text-secondary)', fontFamily: 'monospace' }}>{sessionUuid.slice(0, 8)}</div>
          </div>
          <div style={{ textAlign: 'center' }}>
            <div style={{ fontSize: 10, color: 'var(--color-text-muted)', fontWeight: 800, textTransform: 'uppercase', marginBottom: 2 }}>Status</div>
            {sessionEnded ? (
               <span style={{ background: 'var(--color-border)', color: 'var(--color-text-secondary)', padding: '2px 10px', borderRadius: 4, fontSize: 11, fontWeight: 800, textTransform: 'uppercase' }}>Ended</span>
            ) : (
               <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--color-accent)' }}>
                 <div style={{ width: 6, height: 6, borderRadius: '50%', background: 'var(--color-accent)', animation: 'pulse 1.5s infinite' }} />
                 <span style={{ fontSize: 11, fontWeight: 800, textTransform: 'uppercase' }}>Session Live</span>
               </div>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 24 }}>
          <div style={{ display: 'flex', gap: 12 }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: wsStatus === 'connected' ? 'var(--color-accent-light)' : '#fee2e2', padding: '4px 10px', borderRadius: 6, border: `1px solid ${wsStatus === 'connected' ? 'var(--color-accent)' : 'var(--color-danger)'}` }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: wsStatus === 'connected' ? 'var(--color-accent)' : 'var(--color-danger)' }} />
              <span style={{ fontSize: 11, fontWeight: 700, color: wsStatus === 'connected' ? 'var(--color-accent)' : 'var(--color-danger)' }}>WS</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, background: visionStatus === 'online' ? 'var(--color-accent-light)' : '#fee2e2', padding: '4px 10px', borderRadius: 6, border: `1px solid ${visionStatus === 'online' ? 'var(--color-accent)' : 'var(--color-danger)'}` }}>
              <div style={{ width: 6, height: 6, borderRadius: '50%', background: visionStatus === 'online' ? 'var(--color-accent)' : 'var(--color-danger)' }} />
              <span style={{ fontSize: 11, fontWeight: 700, color: visionStatus === 'online' ? 'var(--color-accent)' : 'var(--color-danger)' }}>Vision</span>
            </div>
          </div>
          <div style={{ width: 64, textAlign: 'right', fontSize: 18, fontWeight: 900, color: 'var(--color-text-primary)', fontFamily: 'monospace' }}>
            {formatDuration(elapsed)}
          </div>
        </div>
      </header>

      {/* Main Grid */}
      <main style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))',
        gap: '24px', padding: '24px', flex: 1
      }}>
        {/* Column 1: Vision */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Visual Attention Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '20px', border: '1px solid var(--color-border)' }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Visual Attention</h3>
            <div style={{
              textAlign: 'center', fontSize: 32, fontWeight: 900, marginBottom: 20,
              color: ATTENTION_COLORS[vision?.attentionState ?? 'UNKNOWN'],
              transition: 'color 0.6s ease'
            }}>
              {vision?.attentionState ?? 'UNKNOWN'}
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px 24px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Presence:</span>
                <span style={{ fontWeight: 700 }}>{vision?.presence ? '\u2713' : '\u2717'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Verified:</span>
                <span style={{ fontWeight: 700 }}>{vision?.faceVerified ? '\u2713' : '\u2717'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Looking at screen:</span>
                <span style={{ fontWeight: 700 }}>{vision?.lookingAtScreen ? '\u2713' : '\u2717'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 13 }}>
                <span style={{ color: 'var(--color-text-secondary)' }}>Frames away:</span>
                <span style={{ fontWeight: 700 }}>{vision?.distractionFrames ?? 0}</span>
              </div>
            </div>
          </section>

          {/* Engagement Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '20px', border: '1px solid var(--color-border)' }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Engagement</h3>
            <Gauge label="Engagement (Raw)" value={vision?.engagementScore ?? 0} color="var(--color-warning)" />
            <Gauge label="Engagement (Display)" value={vision?.engagementScoreUI ?? 0} color="var(--color-accent)" />
            <div style={{ marginTop: 12, fontSize: 11, color: 'var(--color-text-muted)', textAlign: 'right' }}>
              Vision confidence: {((vision?.systemConfidence ?? 0) * 100).toFixed(0)}%
            </div>
          </section>

          {/* Detection Confidence Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '20px', border: '1px solid var(--color-border)' }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Detection Confidence</h3>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
              <MetricChip label="Face" value={vision?.confidence?.face ?? 0} />
              <MetricChip label="Gesture" value={vision?.confidence?.gesture ?? 0} />
              <MetricChip label="Pose" value={vision?.confidence?.pose ?? 0} />
              <MetricChip label="Objects" value={vision?.confidence?.objects ?? 0} />
            </div>
          </section>

          {/* Gesture & Objects Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '20px', border: '1px solid var(--color-border)' }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Current Gesture & Objects</h3>
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 11, color: 'var(--color-text-muted)', fontWeight: 700, marginBottom: 8 }}>LAST GESTURE</div>
              <div style={{ fontSize: 18, fontWeight: 800, color: 'var(--color-primary)' }}>{vision?.gesture ?? 'NONE'}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: 'var(--color-text-muted)', fontWeight: 700, marginBottom: 8 }}>DETECTED OBJECTS</div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                {vision?.detectedObjects?.length > 0 ? vision.detectedObjects.map((obj, i) => (
                  <span key={i} style={{ background: 'var(--color-bg)', padding: '4px 8px', borderRadius: 4, fontSize: 11, border: '1px solid var(--color-border)' }}>{obj}</span>
                )) : <span style={{ color: 'var(--color-text-muted)', fontSize: 12 }}>No objects detected</span>}
              </div>
            </div>
          </section>

          {/* Frame Status Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '12px 20px', border: '1px solid var(--color-border)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
               <h3 style={{ fontSize: 10, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', margin: 0 }}>Frame Status</h3>
               <div style={{ display: 'flex', gap: 8 }}>
                 <StatusChip label="Quality Skip" active={vision?.skipped?.quality} />
                 <StatusChip label="Throttle Skip" active={vision?.skipped?.throttle} />
                 <StatusChip label="Camera Drop" active={vision?.skipped?.camera_drop} />
               </div>
            </div>
          </section>
        </div>

        {/* Column 2: Voice & Emotional State */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Session State Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '20px', border: '1px solid var(--color-border)' }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Session State</h3>
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, marginBottom: 20 }}>
              <div style={{
                padding: '6px 16px', borderRadius: 20, fontSize: 13, fontWeight: 800,
                background: 'var(--color-primary)', color: '#ffffff', textTransform: 'uppercase'
              }}>
                {sessionState.mode}
              </div>
              <div style={{ fontSize: 14, color: 'var(--color-text-secondary)' }}>Turn <span style={{ color: 'var(--color-text-primary)', fontWeight: 700 }}>{sessionState.turn_count}</span></div>
            </div>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 8, fontSize: 13 }}>
                <span>Difficulty Level</span>
                <span style={{ fontWeight: 700 }}>{sessionState.difficulty}/5</span>
              </div>
              <div style={{ display: 'flex', gap: 8 }}>
                {[1, 2, 3, 4, 5].map(lvl => (
                  <div key={lvl} style={{
                    flex: 1, height: 8, borderRadius: 4,
                    background: lvl <= sessionState.difficulty ? 'var(--color-primary)' : 'var(--color-border)'
                  }} />
                ))}
              </div>
            </div>
          </section>

          {/* Emotional State Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '20px', border: '1px solid var(--color-border)' }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Emotional State</h3>
            <div style={{ textAlign: 'center', fontSize: 32, fontWeight: 900, marginBottom: 8, color: MOOD_COLORS[mood.mood] ?? 'var(--color-text-secondary)', textTransform: 'uppercase', transition: 'color 0.6s ease' }}>
              {mood.mood}
            </div>
            <div style={{ marginBottom: 20 }}>
              <div style={{ height: 4, background: 'var(--color-border)', borderRadius: 2, overflow: 'hidden' }}>
                <div style={{
                  width: `${(mood.confidence * 100).toFixed(0)}%`,
                  height: '100%', background: MOOD_COLORS[mood.mood] ?? 'var(--color-text-secondary)',
                  transition: 'width 0.8s cubic-bezier(0.4, 0, 0.2, 1), background 0.6s ease'
                }} />
              </div>
              <div style={{ textAlign: 'right', fontSize: 10, color: 'var(--color-text-muted)', marginTop: 4 }}>
                Confidence: {(mood.confidence * 100).toFixed(0)}%
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
              <Gauge label="Frustration Persistence" value={mood.regulation?.frustration_persistence ?? 0} color="var(--color-danger)" />
              <Gauge label="Stability Persistence" value={mood.regulation?.stability_persistence ?? 0} color="var(--color-accent)" />
              <div style={{ marginBottom: 4 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4, fontSize: 11, fontWeight: 600, color: 'var(--color-text-secondary)' }}>
                  <span>Emotional Trend</span>
                  <span>{mood.regulation?.trend >= 0 ? 'Improving' : 'Declining'}</span>
                </div>
                <div style={{ height: 20, position: 'relative', display: 'flex', alignItems: 'center' }}>
                  <div style={{ width: '100%', height: 2, background: 'var(--color-border)' }} />
                  <div style={{
                    position: 'absolute', width: 12, height: 12, borderRadius: '50%',
                    background: 'var(--color-primary)', border: '2px solid var(--color-bg)',
                    left: `${((mood.regulation?.trend ?? 0) + 1) * 50}%`,
                    transform: 'translateX(-50%)',
                    transition: 'left 0.3s ease'
                  }} />
                  <div style={{ position: 'absolute', left: 0, bottom: -12, fontSize: 8, color: 'var(--color-text-muted)' }}>DECLINING</div>
                  <div style={{ position: 'absolute', right: 0, bottom: -12, fontSize: 8, color: 'var(--color-text-muted)' }}>IMPROVING</div>
                </div>
              </div>
            </div>
          </section>

          {/* Recovery Strategy Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '20px', border: '1px solid var(--color-border)' }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Recovery Strategy</h3>
            <div style={{
              display: 'inline-block', padding: '4px 12px', borderRadius: 6,
              background: 'var(--color-primary-light)', color: 'var(--color-primary)', fontSize: 14, fontWeight: 800,
              textTransform: 'uppercase', marginBottom: 12
            }}>
              {strategy}
            </div>
            <div style={{
              background: 'var(--color-bg)', padding: '12px', borderRadius: 8,
              fontSize: 13, color: 'var(--color-text-secondary)', border: '1px solid var(--color-border)'
            }}>
              {STRATEGY_MAP[strategy] ?? "Active monitoring"}
            </div>
          </section>

          {/* Mood History Card */}
          <section className="monitor-card" style={{ background: 'var(--color-surface)', borderRadius: 12, padding: '20px', border: '1px solid var(--color-border)' }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 16 }}>Mood History (Last 10 turns)</h3>
            <div style={{ display: 'flex', gap: 8, marginBottom: 16 }}>
              {moodHistory.map((m, i) => (
                <div key={i} style={{
                  width: 12, height: 12, borderRadius: '50%',
                  background: MOOD_COLORS[m] ?? 'var(--color-border)',
                  boxShadow: '0 0 10px rgba(0,0,0,0.5)'
                }} />
              ))}
              {Array(Math.max(0, 10 - moodHistory.length)).fill(0).map((_, i) => (
                <div key={`empty-${i}`} style={{ width: 12, height: 12, borderRadius: '50%', background: 'var(--color-border)' }} />
              ))}
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px 16px' }}>
              {Object.entries(MOOD_COLORS).map(([name, color]) => (
                <div key={name} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                  <div style={{ width: 6, height: 6, borderRadius: '50%', background: color }} />
                  <span style={{ fontSize: 9, color: 'var(--color-text-muted)', textTransform: 'capitalize' }}>{name}</span>
                </div>
              ))}
            </div>
          </section>
        </div>

        {/* Column 3: Transcript & Timeline */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
          {/* Live Transcript Card */}
          <section className="monitor-card" style={{
            background: 'var(--color-surface)', borderRadius: 12, border: '1px solid var(--color-border)',
            display: 'flex', flexDirection: 'column', height: '45vh'
          }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', padding: '20px 20px 10px' }}>Live Transcript</h3>
            <div style={{ flex: 1, overflowY: 'auto', padding: '0 20px 20px', display: 'flex', flexDirection: 'column', gap: 12 }}>
              {transcript.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', marginTop: 40, fontSize: 13 }}>Waiting for conversation...</div>
              ) : transcript.map((entry, i) => (
                <div key={i} style={{ alignSelf: entry.speaker === 'lara' ? 'flex-start' : 'flex-end', maxWidth: '85%' }}>
                   <div style={{ fontSize: 9, fontWeight: 700, color: entry.speaker === 'lara' ? 'var(--color-primary)' : 'var(--color-accent)', textTransform: 'uppercase', marginBottom: 2 }}>
                     {entry.speaker === 'lara' ? 'LaRa' : 'Child'}
                   </div>
                   <div style={{
                     background: entry.speaker === 'lara' ? 'var(--color-surface)' : 'var(--color-accent-light)',
                     border: `1px solid ${entry.speaker === 'lara' ? 'var(--color-border)' : 'var(--color-accent)'}`,
                     color: entry.speaker === 'lara' ? 'var(--color-text-primary)' : 'var(--color-text-primary)',
                     padding: '8px 12px', borderRadius: 8, fontSize: 13, lineHeight: 1.4
                   }}>
                     {entry.text}
                   </div>
                   <div style={{ fontSize: 8, color: 'var(--color-text-muted)', textAlign: 'right', marginTop: 2 }}>
                     {new Date(entry.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                   </div>
                </div>
              ))}
              <div ref={transcriptEndRef} />
            </div>
          </section>

          {/* Session Events Card */}
          <section className="monitor-card" style={{
            background: 'var(--color-surface)', borderRadius: 12, border: '1px solid var(--color-border)',
            display: 'flex', flexDirection: 'column', height: '30vh'
          }}>
            <h3 style={{ fontSize: 12, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', padding: '20px 20px 10px' }}>Session Events</h3>
            <div style={{ flex: 1, overflowY: 'auto', padding: '0 20px 20px' }}>
              {events.length === 0 ? (
                <div style={{ textAlign: 'center', color: 'var(--color-text-muted)', marginTop: 20, fontSize: 12 }}>No events logged yet</div>
              ) : events.map((ev, i) => (
                <div key={i} style={{ padding: '8px 0', borderBottom: '1px solid var(--color-border)', fontSize: 12, display: 'flex', gap: 12 }}>
                  <span style={{ color: 'var(--color-text-muted)', fontFamily: 'monospace', fontSize: 10, flexShrink: 0 }}>
                    {new Date(ev.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                  </span>
                  <span style={{ color: 'var(--color-text-primary)' }}>{ev.text}</span>
                </div>
              ))}
            </div>
          </section>
        </div>
      </main>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.4; }
        }
        .monitor-card {
          box-shadow: var(--shadow-md, 0 4px 16px rgba(37,99,235,0.08), 0 2px 8px rgba(0,0,0,0.05));
          transition: box-shadow 0.3s ease;
        }
        .monitor-card:hover {
          box-shadow: var(--shadow-lg, 0 10px 40px rgba(37,99,235,0.12), 0 4px 16px rgba(0,0,0,0.06));
        }
        ::-webkit-scrollbar {
          width: 6px;
        }
        ::-webkit-scrollbar-track {
          background: var(--color-bg);
        }
        ::-webkit-scrollbar-thumb {
          background: var(--color-border);
          border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: var(--color-text-muted);
        }
      `}</style>
    </div>
  );
};

export default LiveMonitorPage;
