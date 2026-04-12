import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AdminLayout from '../../components/dashboard/AdminLayout';
import { UserCircle } from 'lucide-react';
import { getStoredUser } from '../../services/authService';

export default function AdminProfile() {
    const navigate = useNavigate();
    const user = getStoredUser();

    useEffect(() => {
        if (!user || user.role !== 'ROLE_ADMIN') {
            navigate('/login');
        }
    }, [user, navigate]);

    if (!user) return null;

    return (
        <AdminLayout 
            title="Admin Profile" 
            subtitle="Manage your platform administrator account preferences."
        >
            <div className="clinical-panel" style={{ maxWidth: '600px' }}>
                <div className="clinical-panel__header" style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '16px' }}>
                    <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                        <UserCircle size={48} color="var(--color-primary)" />
                        <div>
                            <h3 className="clinical-panel__title" style={{ fontSize: '20px' }}>{user.name || 'Administrator'}</h3>
                            <p style={{ color: 'var(--color-text-muted)', fontSize: '14px', marginTop: '4px' }}>Platform Admin</p>
                        </div>
                    </div>
                </div>
                <div style={{ marginTop: '24px', display: 'flex', flexDirection: 'column', gap: '16px' }}>
                    <div>
                        <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '8px' }}>Email Address</label>
                        <div style={{ padding: '12px 16px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', color: 'var(--color-text-primary)' }}>
                            {user.email}
                        </div>
                    </div>
                    <div>
                        <label style={{ display: 'block', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '8px' }}>Role</label>
                        <div style={{ padding: '12px 16px', background: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0', color: 'var(--color-text-primary)' }}>
                            {user.role}
                        </div>
                    </div>
                </div>
            </div>
        </AdminLayout>
    );
}
