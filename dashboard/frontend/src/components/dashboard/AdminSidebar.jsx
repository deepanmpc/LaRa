import { useNavigate, useLocation } from 'react-router-dom';
import { logout, getStoredUser } from '../../services/authService';
import { 
    LayoutDashboard, 
    Activity, 
    BrainCircuit, 
    Download, 
    Users, 
    Bell, 
    TrendingUp,
    UserCircle,
    UserCheck
} from 'lucide-react';

const ADMIN_NAV_ITEMS = [
    {
        id: 'dashboard',
        path: '/admin',
        label: "Dashboard",
        icon: <LayoutDashboard size={18} />,
    },
    {
        id: 'system',
        path: '/admin/system',
        label: 'System Monitoring',
        icon: <Activity size={18} />,
    },
    {
        id: 'model',
        path: '/admin/model',
        label: 'Model Evaluation',
        icon: <BrainCircuit size={18} />,
    },
    {
        id: 'population',
        path: '/admin/population',
        label: 'Population Analytics',
        icon: <TrendingUp size={18} />,
    },
    {
        id: 'alerts',
        path: '/admin/alerts',
        label: 'Alert Monitoring',
        icon: <Bell size={18} />,
    },
    {
        id: 'dataset',
        path: '/admin/dataset',
        label: 'Dataset Export',
        icon: <Download size={18} />,
    },
    {
        id: 'users',
        path: '/admin/users',
        label: 'User Management',
        icon: <Users size={18} />,
    },
    {
        id: 'clinicians',
        path: '/admin/clinicians',
        label: 'Clinician Approvals',
        icon: <UserCheck size={18} />,
    },
];

export default function AdminSidebar() {
    const navigate = useNavigate();
    const location = useLocation();
    const user = getStoredUser();

    const isActive = (path) => location.pathname === path;

    const handleSignOut = () => {
        logout();
        navigate('/login');
    };

    return (
        <aside className="sidebar">
            <div className="sidebar-logo">
                <div className="sidebar-logo-icon" style={{ background: 'var(--color-primary)' }}>A</div>
                <div className="sidebar-logo-text">La<span>Ra</span> Admin</div>
            </div>
            <div className="sidebar-role-badge" style={{ background: '#fef2f2', color: '#991b1b' }}>Platform Operations</div>

            <nav className="sidebar-nav">
                <div className="sidebar-nav-label">Core Operations</div>
                {ADMIN_NAV_ITEMS.map((item) => (
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
                    className={`sidebar-nav-item ${isActive('/admin/profile') ? 'active' : ''}`}
                    onClick={() => navigate('/admin/profile')}
                >
                    <UserCircle size={18} />
                    Profile
                </button>
            </nav>

            <div className="sidebar-footer">
                <div style={{ padding: '10px 14px', marginBottom: 8 }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{user?.name || 'Administrator'}</div>
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
