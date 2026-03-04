import { useNavigate } from 'react-router-dom';
import { logout, getStoredUser } from '../services/authService';

export default function ClinicianPending() {
    const navigate = useNavigate();
    const user = getStoredUser();

    const handleSignOut = () => {
        logout();
        navigate('/login');
    };

    return (
        <div className="pending-page">
            <div className="pending-card">
                <div className="pending-icon">⏳</div>
                <h1 className="pending-title">Account Under Review</h1>
                <p className="pending-message">
                    Welcome, <strong>{user?.name || 'Clinician'}</strong>! Your clinician account
                    has been submitted and is currently awaiting admin approval.
                    You will be notified once your credentials have been reviewed.
                </p>
                <div className="pending-status-pill">
                    <span style={{ width: 8, height: 8, background: '#f59e0b', borderRadius: '50%', display: 'inline-block' }}></span>
                    Awaiting Admin Approval
                </div>
                <p style={{ fontSize: 13, color: 'var(--color-text-muted)', marginBottom: 28 }}>
                    Registered as: <strong>{user?.email}</strong>
                </p>
                <button className="btn-secondary" onClick={handleSignOut}>
                    Sign Out
                </button>
            </div>
        </div>
    );
}
