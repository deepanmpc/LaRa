import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import { getStoredUser } from '../services/authService';
import api from '../services/api';
import ChildSwitcher from '../components/dashboard/ChildSwitcher';

// ─── Helpers ────────────────────────────────────
function ProgressBar({ value, variant = 'primary' }) {
    const [width, setWidth] = useState(0);
    useEffect(() => {
        const timer = setTimeout(() => setWidth(value), 100);
        return () => clearTimeout(timer);
    }, [value]);
    return (
        <div className="progress-bar">
            <div className={`progress-fill ${variant}`} style={{ width: `${width}%` }} />
        </div>
    );
}

function MoodDot({ color, label, percent }) {
    return (
        <div className="mood-row">
            <div className="mood-dot" style={{ background: color }} />
            <span className="mood-label">{label}</span>
            <span className="mood-percent">{percent}%</span>
        </div>
    );
}

// ─── Card Skeleton ───────────────────────────────
function SkeletonCard() {
    return (
        <div className="card">
            <div className="skeleton" style={{ height: 20, width: '60%', marginBottom: 16 }} />
            <div className="skeleton" style={{ height: 16, width: '100%', marginBottom: 10 }} />
            <div className="skeleton" style={{ height: 16, width: '80%', marginBottom: 10 }} />
            <div className="skeleton" style={{ height: 16, width: '90%' }} />
        </div>
    );
}

// ─── Today's Summary Card ────────────────────────
function SessionSummaryCard({ data }) {
    if (!data) return <SkeletonCard />;
    return (
        <div className="card">
            <div className="card-header">
                <div className="card-title">
                    <div className="card-icon blue">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
                            <line x1="16" y1="2" x2="16" y2="6" />
                            <line x1="8" y1="2" x2="8" y2="6" />
                            <line x1="3" y1="10" x2="21" y2="10" />
                        </svg>
                    </div>
                    Today's Summary
                </div>
                <span className="card-badge green">Week {data.totalSessionsThisWeek || 0}/5</span>
            </div>

            <div className="stat-grid" style={{ marginBottom: 20 }}>
                <div className="stat-item">
                    <div className="stat-item-value">{data.totalSessionsThisWeek || 0}</div>
                    <div className="stat-item-label">Sessions This Week</div>
                </div>
                <div className="stat-item">
                    <div className="stat-item-value">{data.todaySessionDuration || '0 minutes'}</div>
                    <div className="stat-item-label">Today's Duration</div>
                </div>
                <div className="stat-item">
                    <div className="stat-item-value">{data.activitiesCompletedToday || 0}</div>
                    <div className="stat-item-label">Activities Today</div>
                </div>
                <div className="stat-item">
                    <div className="stat-item-value">{data.totalSessionsAllTime || 0}</div>
                    <div className="stat-item-label">All-Time Sessions</div>
                </div>
            </div>

            <div className="progress-group">
                <div className="progress-item">
                    <div className="progress-label-row">
                        <span className="progress-label">Weekly Goal Progress</span>
                        <span className="progress-value">{data.weeklyGoalProgress || 0}%</span>
                    </div>
                    <ProgressBar value={data.weeklyGoalProgress || 0} variant="primary" />
                </div>
            </div>

            {(data.lastActivityCompleted || data.nextScheduledSession) && (
                <div style={{ marginTop: 16, padding: '12px 14px', background: 'var(--color-bg)', borderRadius: 12 }}>
                    {data.lastActivityCompleted && (
                        <>
                            <div style={{ fontSize: 11, color: 'var(--color-text-muted)', fontWeight: 600, marginBottom: 3 }}>LAST ACTIVITY</div>
                            <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{data.lastActivityCompleted}</div>
                        </>
                    )}
                    {data.nextScheduledSession && (
                        <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: data.lastActivityCompleted ? 8 : 0 }}>
                            Next: {data.nextScheduledSession}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

// ─── Emotional Wellbeing Card ────────────────────
function EmotionalCard({ data }) {
    if (!data) return <SkeletonCard />;

    const moodColors = {
        Happy: '#f59e0b',
        Calm: '#3b82f6',
        Focused: '#8b5cf6',
        Anxious: '#ef4444',
        Frustrated: '#f97316',
    };

    const breakdown = data.emotionBreakdown || {};

    return (
        <div className="card">
            <div className="card-header">
                <div className="card-title">
                    <div className="card-icon green">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <path d="M20.84 4.61a5.5 5.5 0 00-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 00-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 000-7.78z" />
                        </svg>
                    </div>
                    Emotional Wellbeing
                </div>
                {data.moodTrend && <span className="card-badge green">{data.moodTrend}</span>}
            </div>

            <div className="stat-grid" style={{ marginBottom: 20 }}>
                <div className="stat-item">
                    <div className="stat-item-value" style={{ color: 'var(--color-accent)' }}>{data.overallMoodScore || '--'}</div>
                    <div className="stat-item-label">Mood Score</div>
                </div>
                <div className="stat-item">
                    <div className="stat-item-value">{data.primaryEmotion || '--'}</div>
                    <div className="stat-item-label">Primary Emotion</div>
                </div>
                {data.selfRegulationScore != null && (
                    <div className="stat-item">
                        <div className="stat-item-value">{data.selfRegulationScore}</div>
                        <div className="stat-item-label">Self-Regulation</div>
                    </div>
                )}
                {data.anxietyLevel != null && (
                    <div className="stat-item">
                        <div className="stat-item-value">{data.anxietyLevel}</div>
                        <div className="stat-item-label">Anxiety Level</div>
                    </div>
                )}
            </div>

            {Object.keys(breakdown).length > 0 && (
                <>
                    <div style={{ marginBottom: 8, fontSize: 11, fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                        Emotion Breakdown
                    </div>
                    {Object.entries(breakdown).map(([emotion, percent]) => (
                        <MoodDot key={emotion} color={moodColors[emotion] || '#94a3b8'} label={emotion} percent={percent} />
                    ))}
                </>
            )}

            {data.emotionStability != null && (
                <div className="progress-group" style={{ marginTop: 16 }}>
                    <div className="progress-item">
                        <div className="progress-label-row">
                            <span className="progress-label">Stability Score</span>
                            <span className="progress-value">{data.emotionStability}%</span>
                        </div>
                        <ProgressBar value={data.emotionStability} variant="green" />
                    </div>
                </div>
            )}
        </div>
    );
}

// ─── Engagement & Focus Card ─────────────────────
function EngagementCard({ data }) {
    if (!data) return <SkeletonCard />;

    return (
        <div className="card dashboard-grid-full">
            <div className="card-header">
                <div className="card-title">
                    <div className="card-icon amber">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
                        </svg>
                    </div>
                    Engagement & Focus
                </div>
                {data.participationLevel && <span className="card-badge blue">{data.participationLevel} Participation</span>}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: 20 }}>
                {/* Left col: stats */}
                <div>
                    <div className="stat-grid">
                        <div className="stat-item">
                            <div className="stat-item-value" style={{ color: 'var(--color-primary)' }}>{data.focusScore || '--'}</div>
                            <div className="stat-item-label">Focus Score</div>
                        </div>
                        {data.attentionSpanMinutes != null && (
                            <div className="stat-item">
                                <div className="stat-item-value">{data.attentionSpanMinutes}m</div>
                                <div className="stat-item-label">Attention Span</div>
                            </div>
                        )}
                        {data.taskCompletionRate != null && (
                            <div className="stat-item">
                                <div className="stat-item-value">{data.taskCompletionRate}%</div>
                                <div className="stat-item-label">Task Completion</div>
                            </div>
                        )}
                        {data.responsiveness != null && (
                            <div className="stat-item">
                                <div className="stat-item-value">{data.responsiveness}</div>
                                <div className="stat-item-label">Responsiveness</div>
                            </div>
                        )}
                    </div>
                </div>

                {/* Mid col: progress bars */}
                <div className="progress-group">
                    <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
                        Skill Breakdown
                    </div>
                    <div className="progress-item">
                        <div className="progress-label-row">
                            <span className="progress-label">Focus Score</span>
                            <span className="progress-value">{data.focusScore || 0}%</span>
                        </div>
                        <ProgressBar value={data.focusScore || 0} variant="primary" />
                    </div>
                    {data.taskCompletionRate != null && (
                        <div className="progress-item">
                            <div className="progress-label-row">
                                <span className="progress-label">Task Completion</span>
                                <span className="progress-value">{data.taskCompletionRate}%</span>
                            </div>
                            <ProgressBar value={data.taskCompletionRate} variant="green" />
                        </div>
                    )}
                    {data.collaborationScore != null && (
                        <div className="progress-item">
                            <div className="progress-label-row">
                                <span className="progress-label">Collaboration</span>
                                <span className="progress-value">{data.collaborationScore}%</span>
                            </div>
                            <ProgressBar value={data.collaborationScore} variant="amber" />
                        </div>
                    )}
                    {data.initiativeTaking != null && (
                        <div className="progress-item">
                            <div className="progress-label-row">
                                <span className="progress-label">Initiative</span>
                                <span className="progress-value">{data.initiativeTaking}%</span>
                            </div>
                            <ProgressBar value={data.initiativeTaking} variant="primary" />
                        </div>
                    )}
                </div>

                {/* Right col: top activities */}
                <div>
                    <div style={{ fontSize: 11, fontWeight: 700, color: 'var(--color-text-muted)', textTransform: 'uppercase', letterSpacing: '0.08em', marginBottom: 12 }}>
                        Top Activities
                    </div>
                    <div className="activity-list">
                        {data.topActivities && data.topActivities.length > 0 ? (
                            data.topActivities.map((activity, idx) => (
                                <div key={idx} className="activity-item">
                                    <span className="activity-rank">#{idx + 1}</span>
                                    <span className="activity-name">{activity.name}</span>
                                    <span className="activity-score">{activity.score}%</span>
                                </div>
                            ))
                        ) : (
                            <div style={{ fontSize: 13, color: 'var(--color-text-muted)', padding: '12px 0' }}>No activity data yet</div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}

// ─── Main Family Dashboard ───────────────────────
export default function FamilyDashboard() {
    const { childId } = useParams();
    const navigate = useNavigate();
    const [activeNav, setActiveNav] = useState('summary');
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeSessionUuid, setActiveSessionUuid] = useState(localStorage.getItem(`activeSession_${childId}`) || null);
    const user = getStoredUser();

    const now = new Date();
    const dateStr = now.toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    const hour = now.getHours();
    const greeting = hour < 12 ? 'Good morning' : hour < 17 ? 'Good afternoon' : 'Good evening';

    useEffect(() => {
        const fetchDashboard = async () => {
            try {
                setLoading(true);
                const response = await api.get(`/family/dashboard/${childId}`);
                setDashboardData(response.data);
                setError('');
            } catch (err) {
                console.error('Failed to load dashboard data', err);
                setError('Failed to load dashboard data. Please try again.');
            } finally {
                setLoading(false);
            }
        };
        if (childId) {
            fetchDashboard();
            const stored = localStorage.getItem(`activeSession_${childId}`);
            if (stored) setActiveSessionUuid(stored);
        }
    }, [childId]);

    // Handle Start Session logic when Sidebar option is clicked
    useEffect(() => {
        if (activeNav === 'session') {
            const startSession = async () => {
                try {
                    const res = await api.post('/family/session/start', { childId });
                    const sessionUuid = res.data?.sessionUuid;
                    if (sessionUuid) {
                        localStorage.setItem(`activeSession_${childId}`, sessionUuid);
                        setActiveSessionUuid(sessionUuid);
                        navigate(`/voice-session/${childId}/${sessionUuid}`);
                    }
                } catch (err) {
                    console.error('Failed to start session', err);
                    alert('Failed to start session. Please try again.');
                } finally {
                    setActiveNav('summary'); // Reset nav state
                }
            };
            startSession();
        } else if (activeNav === 'live-monitor') {
            if (activeSessionUuid) {
                window.open(`/live-monitor/${childId}/${activeSessionUuid}`, '_blank');
            } else {
                alert('No active session currently tracking.');
            }
            setActiveNav('summary');
        }
    }, [activeNav, childId, navigate, activeSessionUuid]);

    const child = dashboardData?.childProfile;
    const session = dashboardData?.sessionSummary;
    const emotional = dashboardData?.emotionalMetrics;
    const engagement = dashboardData?.engagementMetrics;

    return (
        <div className="dashboard-layout">
            <Sidebar activeItem={activeNav} onNavClick={setActiveNav} />

            <main className="dashboard-main">
                <div className="dashboard-header">
                    <div className="dashboard-header-top">
                        <div>
                            <div className="dashboard-greeting">
                                {greeting}, <span>{user?.name?.split(' ')[0] || 'there'}</span> 👋
                            </div>
                            <div className="dashboard-date">{dateStr}</div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                            <ChildSwitcher currentChildId={childId} />
                            <div className="date-picker">
                                <span>Today, {new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}</span>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2" /><line x1="16" y1="2" x2="16" y2="6" /><line x1="8" y1="2" x2="8" y2="6" /><line x1="3" y1="10" x2="21" y2="10" />
                                </svg>
                            </div>
                        </div>
                    </div>

                    {/* Child Header Card */}
                    {loading ? (
                        <div className="child-header-card">
                            <div className="child-avatar">...</div>
                            <div className="child-info">
                                <div className="skeleton" style={{ height: 24, width: 200, marginBottom: 8, background: 'rgba(255,255,255,0.2)' }} />
                                <div className="skeleton" style={{ height: 14, width: 300, background: 'rgba(255,255,255,0.15)' }} />
                            </div>
                        </div>
                    ) : child ? (
                        <div className="child-header-card">
                            <div style={{ display: 'flex', alignItems: 'center', gap: 20, flex: 1 }}>
                                <div className="child-avatar">
                                    {child.name?.charAt(0) || 'A'}
                                </div>
                                <div className="child-info">
                                    <div className="child-name">{child.name}</div>
                                    <div className="child-meta">
                                        <span className="child-meta-item">
                                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="8" r="4" /><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" /></svg>
                                            Age {child.age} · {child.gradeLevel}
                                        </span>
                                        <span className="child-meta-item" style={{ color: child.therapistAssigned === 'None Assigned' ? '#ef4444' : 'inherit', fontWeight: child.therapistAssigned === 'None Assigned' ? 600 : 400 }}>
                                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07 19.5 19.5 0 01-6-6A19.79 19.79 0 012.12 4.18 2 2 0 014.11 2h3a2 2 0 012 1.72c.127.96.361 1.903.7 2.81a2 2 0 01-.45 2.11L8.09 9.91a16 16 0 006 6l1.27-1.27a2 2 0 012.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0122 16.92z" /></svg>
                                            {child.therapistAssigned === 'None Assigned' ? 'Clinician Not Assigned' : child.therapistAssigned}
                                        </span>
                                        <span className="child-meta-item">
                                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>
                                            Last session: {child.lastSessionTime}
                                        </span>
                                    </div>
                                </div>
                            </div>

                            <div className="child-header-stats">
                                <div className="child-stat">
                                    <div className="child-stat-value">{session?.totalSessionsThisWeek || 0}</div>
                                    <div className="child-stat-label">This Week</div>
                                </div>
                                <div className="child-stat">
                                    <div className="child-stat-value">{emotional?.overallMoodScore || '--'}</div>
                                    <div className="child-stat-label">Mood Score</div>
                                </div>
                                <div className="child-stat">
                                    <div className="child-stat-value">{engagement?.focusScore || '--'}</div>
                                    <div className="child-stat-label">Focus Score</div>
                                </div>
                            </div>

                            <div style={{ flexShrink: 0, display: 'flex', flexDirection: 'column', gap: 10 }}>
                                <button
                                    className="btn btn-secondary"
                                    disabled={!activeSessionUuid}
                                    style={{
                                        padding: '12px 24px',
                                        fontSize: 14,
                                        fontWeight: 800,
                                        borderRadius: 12,
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: 10,
                                        background: activeSessionUuid ? '#2563eb' : '#f1f5f9',
                                        color: activeSessionUuid ? 'white' : '#94a3b8',
                                        border: activeSessionUuid ? 'none' : '1px solid #e2e8f0',
                                        cursor: activeSessionUuid ? 'pointer' : 'not-allowed',
                                        transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                                        boxShadow: activeSessionUuid ? '0 8px 24px rgba(37, 99, 235, 0.35)' : 'none',
                                        animation: activeSessionUuid ? 'pulse-blue 2s infinite' : 'none'
                                    }}
                                    onClick={() => window.open(`/live-monitor/${childId}/${activeSessionUuid}`, '_blank')}
                                >
                                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
                                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                                        <circle cx="12" cy="12" r="3" />
                                    </svg>
                                    LIVE TRACKING
                                </button>
                                
                                <style>{`
                                    @keyframes pulse-blue {
                                        0% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0.6); }
                                        70% { box-shadow: 0 0 0 10px rgba(37, 99, 235, 0); }
                                        100% { box-shadow: 0 0 0 0 rgba(37, 99, 235, 0); }
                                    }
                                `}</style>
                                
                                {child.statusBadge && (
                                    <div className="status-badge-doing-well">
                                        <div className="status-dot"></div>
                                        {child.statusBadge}
                                    </div>
                                )}
                                {child.currentFocus && (
                                    <div style={{ fontSize: 11, opacity: 0.7, textAlign: 'center' }}>
                                        Focus: {child.currentFocus}
                                    </div>
                                )}
                            </div>
                        </div>
                    ) : null}

                    {error && (
                        <div className="error-message" style={{ marginBottom: 0 }}>{error}</div>
                    )}
                </div>

                <div className="dashboard-content">
                    <div className="dashboard-grid">
                        <SessionSummaryCard data={session} />
                        <EmotionalCard data={emotional} />
                        <EngagementCard data={engagement} />
                    </div>
                </div>
            </main>
        </div>
    );
}
