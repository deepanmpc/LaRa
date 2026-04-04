import { useNavigate } from 'react-router-dom';

export default function ChildCard({ child }) {
    const navigate = useNavigate();

    const avatarColor = child.avatarColor || '#7c3aed';

    const getBadgeStyle = (badge) => {
        if (!badge) return {};
        if (badge === 'Doing Well') return { background: '#dcfce7', color: '#16a34a', border: '1px solid #bbf7d0' };
        if (badge === 'Steady Progress') return { background: '#fef9c3', color: '#ca8a04', border: '1px solid #fde68a' };
        return { background: '#fecaca', color: '#dc2626', border: '1px solid #fca5a5' };
    };

    return (
        <div
            className="card child-selector-card"
            onClick={() => navigate(`/dashboard/family/${child.id}`)}
            style={{ cursor: 'pointer', transition: 'transform 0.2s, box-shadow 0.2s', border: '1px solid transparent', display: 'flex', flexDirection: 'column', height: '100%' }}
            onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'scale(1.02)';
                e.currentTarget.style.borderColor = 'var(--color-primary)';
                e.currentTarget.style.boxShadow = '0 10px 25px rgba(0,0,0,0.05)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'scale(1)';
                e.currentTarget.style.borderColor = 'transparent';
                e.currentTarget.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05)';
            }}
        >
            <div style={{ display: 'flex', alignItems: 'center', gap: 16, flex: 1, position: 'relative' }}>
                <div className="child-avatar" style={{ width: 48, height: 48, fontSize: 20, background: avatarColor }}>
                    {child.name.charAt(0)}
                </div>
                <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <h3 style={{ margin: 0, fontSize: 18, color: 'var(--color-text-primary)' }}>{child.name}</h3>
                        {child.statusBadge && (
                            <span style={{ fontSize: 10, padding: '2px 8px', borderRadius: 12, fontWeight: 600, ...getBadgeStyle(child.statusBadge) }}>
                                {child.statusBadge}
                            </span>
                        )}
                    </div>
                    <div style={{ fontSize: 13, color: 'var(--color-text-muted)', marginTop: 4 }}>
                        Age {child.age} • {child.gradeLevel || 'Grade ' + child.grade}
                    </div>
                    {child.diagnosis && (
                        <div style={{ fontSize: 12, color: 'var(--color-primary)', marginTop: 2 }}>
                            {child.diagnosis}
                        </div>
                    )}
                </div>
                <div style={{ display: 'flex', gap: 4 }}>
                    {child.onEdit && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                child.onEdit(child);
                            }}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: 'var(--color-text-muted)',
                                cursor: 'pointer',
                                padding: '4px',
                                borderRadius: '4px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'color 0.2s, background 0.2s'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = 'var(--color-primary)';
                                e.currentTarget.style.background = 'var(--color-bg)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = 'var(--color-text-muted)';
                                e.currentTarget.style.background = 'none';
                            }}
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" /><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                            </svg>
                        </button>
                    )}
                    {child.onDelete && (
                        <button
                            onClick={(e) => {
                                e.stopPropagation();
                                child.onDelete(child.id, child.name);
                            }}
                            style={{
                                background: 'none',
                                border: 'none',
                                color: 'var(--color-text-muted)',
                                cursor: 'pointer',
                                padding: '4px',
                                borderRadius: '4px',
                                display: 'flex',
                                alignItems: 'center',
                                justifyContent: 'center',
                                transition: 'color 0.2s, background 0.2s'
                            }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.color = '#ef4444';
                                e.currentTarget.style.background = '#fee2e2';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.color = 'var(--color-text-muted)';
                                e.currentTarget.style.background = 'none';
                            }}
                        >
                            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M3 6h18" /><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6" /><path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2" />
                            </svg>
                        </button>
                    )}
                </div>
            </div>
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--color-border)', fontSize: 12, color: 'var(--color-text-muted)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
                    </svg>
                    {child.lastSessionDate || child.lastSessionAt || 'No sessions yet'}
                </span>
                {child.currentFocusArea && (
                    <span style={{ fontSize: 11, padding: '2px 6px', borderRadius: 6, background: 'var(--color-bg)', color: 'var(--color-text-muted)' }}>
                        Focus: {child.currentFocusArea}
                    </span>
                )}
            </div>
        </div>
    );
}
