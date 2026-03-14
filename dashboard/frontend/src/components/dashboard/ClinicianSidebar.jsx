import { useNavigate, useLocation } from 'react-router-dom';
import { logout, getStoredUser } from '../../services/authService';

const CLINICIAN_NAV_ITEMS = [
    {
        id: 'dashboard',
        path: '/dashboard/clinical',
        label: "Dashboard",
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
        id: 'students',
        path: '/dashboard/clinical/students',
        label: 'Students',
        icon: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M23 21v-2a4 4 0 00-3-3.87" />
                <path d="M16 3.13a4 4 0 010 7.75" />
            </svg>
        ),
    },
    {
        id: 'sessions',
        path: '/dashboard/clinical/sessions',
        label: 'Sessions',
        icon: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <polyline points="12 6 12 12 16 14" />
            </svg>
        ),
    },
    {
        id: 'reports',
        path: '/dashboard/clinical/reports',
        label: 'Reports',
        icon: (
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <polyline points="14 2 14 8 20 8" />
                <line x1="16" y1="13" x2="8" y2="13" />
                <line x1="16" y1="17" x2="8" y2="17" />
                <polyline points="10 9 9 9 8 9" />
            </svg>
        ),
    },
];

export default function ClinicianSidebar() {
    const navigate = useNavigate();
    const location = useLocation();
    const user = getStoredUser();

    // Exact match only — prevents partial path collisions (e.g. /students matching /sessions)
    const isActive = (path) => location.pathname === path;

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
            <div className="sidebar-role-badge" style={{ background: '#e0f2fe', color: '#0369a1' }}>Clinician View</div>

            <nav className="sidebar-nav">
                <div className="sidebar-nav-label">Navigation</div>
                {CLINICIAN_NAV_ITEMS.map((item) => (
                    <button
                        key={item.id}
                        className={`sidebar-nav-item ${isActive(item.path) ? 'active' : ''}`}
                        onClick={() => navigate(item.path)}
                    >
                        {item.icon}
                        {item.label}
                    </button>
                ))}

                <div className="sidebar-nav-label">Account</div>
                <button
                    className={`sidebar-nav-item ${isActive('/dashboard/profile') ? 'active' : ''}`}
                    onClick={() => navigate('/dashboard/profile')}
                >
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                        <circle cx="12" cy="7" r="4" />
                    </svg>
                    Profile
                </button>
            </nav>

            <div className="sidebar-footer">
                <div style={{ padding: '10px 14px', marginBottom: 8 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{user?.name || 'Dr. Smith'}</div>
                    <div style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 2 }}>{user?.email || ''}</div>
                </div>
                <button
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
