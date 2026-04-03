import { useNavigate, useLocation } from 'react-router-dom';
import { logout, getStoredUser } from '../services/authService';

const NAV_ITEMS = [
    {
        id: 'summary',
        label: "Today's Summary",
        icon: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="7" height="7" rx="1" />
                <rect x="14" y="3" width="7" height="7" rx="1" />
                <rect x="14" y="14" width="7" height="7" rx="1" />
                <rect x="3" y="14" width="7" height="7" rx="1" />
            </svg>
        ),
    },
    {
        id: 'session',
        label: 'Start Session',
        icon: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polygon points="10,8 16,12 10,16" />
            </svg>
        ),
    },
    {
        id: 'live-monitor',
        label: 'Live Monitor',
        icon: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
            </svg>
        ),
    },
];

export default function Sidebar({ activeItem, onNavClick }) {
    const navigate = useNavigate();
    const location = useLocation();
    const user = getStoredUser();

    // Profile active state
    const isProfileActive = location.pathname === '/dashboard/profile';

    const handleSignOut = () => {
        logout();
        navigate('/login');
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon">L</div>
                <div className="sidebar-logo-text">La<span>Ra</span> Care</div>
            </div>
            <div className="sidebar-role-badge">Family View</div>

            <nav className="sidebar-nav">
                <div className="sidebar-nav-label">Navigation</div>
                {NAV_ITEMS.map((item) => (
                    <button
                        key={item.id}
                        id={`sidebar-nav-${item.id}`}
                        className={`sidebar-nav-item ${activeItem === item.id ? 'active' : ''}`}
                        onClick={() => onNavClick && onNavClick(item.id)}
                    >
                        {item.icon}
                        {item.label}
                    </button>
                ))}

                <div className="sidebar-nav-label">Account</div>
                <button
                    id="sidebar-nav-profile"
                    className={`sidebar-nav-item ${isProfileActive ? 'active' : ''}`}
                    onClick={() => navigate('/dashboard/profile')}
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                    </svg>
                    Profile
                </button>

                <div className="sidebar-nav-label">Support</div>
                <button
                    id="sidebar-nav-resources"
                    className="sidebar-nav-item"
                    onClick={() => { }}
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 20h9" />
                        <path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
                    </svg>
                    Resources
                </button>
            </nav>

            <div className="sidebar-footer">
                <div style={{ padding: '10px 14px', marginBottom: 8 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{user?.name || 'Family Member'}</div>
                    <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 2 }}>{user?.email || ''}</div>
                </div>
                <button
                    id="sidebar-signout-btn"
                    className="sidebar-signout-btn"
                    onClick={handleSignOut}
                >
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
                        <polyline points="16,17 21,12 16,7" />
                        <line x1="21" y1="12" x2="9" y2="12" />
                    </svg>
                    Sign Out
                </button>
            </div>
        </aside>
    );
}
