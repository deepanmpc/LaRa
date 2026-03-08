export default function AddChildCard({ onClick }) {
    return (
        <div
            className="card child-selector-card add-child-card"
            onClick={onClick}
            style={{
                cursor: 'pointer',
                border: '2px dashed var(--color-border)',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'transparent',
                boxShadow: 'none',
                minHeight: '160px',
                transition: 'background 0.2s, border-color 0.2s'
            }}
            onMouseEnter={(e) => {
                e.currentTarget.style.background = 'rgba(14, 165, 233, 0.05)';
                e.currentTarget.style.borderColor = 'var(--color-primary)';
            }}
            onMouseLeave={(e) => {
                e.currentTarget.style.background = 'transparent';
                e.currentTarget.style.borderColor = 'var(--color-border)';
            }}
        >
            <div style={{
                width: 48, height: 48,
                borderRadius: '50%',
                background: 'var(--color-bg)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                color: 'var(--color-primary)',
                marginBottom: 12
            }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
            </div>
            <div style={{ fontWeight: 600, color: 'var(--color-primary)' }}>Add Child</div>
        </div>
    );
}
