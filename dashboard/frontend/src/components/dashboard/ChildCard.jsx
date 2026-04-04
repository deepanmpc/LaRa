import { useNavigate } from 'react-router-dom';

export default function ChildCard({ child }) {
    const navigate = useNavigate();

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
                <div className="child-avatar" style={{ width: 48, height: 48, fontSize: 20 }}>
                    {child.name.charAt(0)}
                </div>
                <div style={{ flex: 1 }}>
                    <h3 style={{ margin: 0, fontSize: 18, color: 'var(--color-text-primary)' }}>{child.name}</h3>
                    <div style={{ fontSize: 13, color: 'var(--color-text-muted)', marginTop: 4 }}>
                        Age {child.age} • {child.gradeLevel || 'Grade ' + child.grade}
                    </div>
                </div>
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
            <div style={{ marginTop: 20, paddingTop: 16, borderTop: '1px solid var(--color-border)', fontSize: 12, color: 'var(--color-text-muted)' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" />
                    </svg>
                    Last session: {child.lastSessionDate || child.lastSessionTime || 'No sessions yet'}
                </span>
            </div>
        </div>
    );
}
