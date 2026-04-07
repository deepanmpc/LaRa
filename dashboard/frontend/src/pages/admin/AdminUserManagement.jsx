import { useState, useEffect } from 'react';
import AdminLayout from '../../components/dashboard/AdminLayout';
import api from '../../services/api';
import { 
    CheckCircle, 
    XCircle, 
    Trash2, 
    Shield, 
    Mail,
    Search
} from 'lucide-react';

export default function AdminUserManagement() {
    const [users, setUsers] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');

    const fetchUsers = async () => {
        try {
            const res = await api.get('/api/admin/users');
            setUsers(res.data);
        } catch (err) {
            console.error('Failed to fetch users', err);
        }
    };

    useEffect(() => {
        // eslint-disable-next-line
        fetchUsers();
    }, []);

    const handleApprove = async (id) => {
        if (!confirm('Approve this user?')) return;
        try {
            await api.post(`/api/admin/users/${id}/approve`);
            fetchUsers();
        } catch (err) { 
            console.error(err);
            alert('Approval failed'); 
        }
    };

    const handleSuspend = async (id) => {
        if (!confirm('Suspend this user?')) return;
        try {
            await api.post(`/api/admin/users/${id}/suspend`);
            fetchUsers();
        } catch (err) { 
            console.error(err);
            alert('Suspension failed'); 
        }
    };

    const handleDelete = async (id) => {
        if (!confirm('PERMANENTLY DELETE this user? This cannot be undone.')) return;
        try {
            await api.delete(`/api/admin/users/${id}`);
            fetchUsers();
        } catch (err) { 
            console.error(err);
            alert('Deletion failed'); 
        }
    };

    const filteredUsers = users.filter(u => 
        u.name?.toLowerCase().includes(searchTerm.toLowerCase()) || 
        u.email?.toLowerCase().includes(searchTerm.toLowerCase())
    );

    return (
        <AdminLayout title="User Management" subtitle="Review and moderate platform access for clinicians and staff.">
            <article className="clinical-panel" style={{ padding: 0 }}>
                <div className="clinical-panel__header" style={{ padding: '24px', borderBottom: '1px solid #f1f5f9', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div className="search-box" style={{ position: 'relative', width: '300px' }}>
                        <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
                        <input 
                            type="text" 
                            placeholder="Search by name or email..." 
                            style={{ width: '100%', padding: '10px 12px 10px 40px', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '13px' }}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                        />
                    </div>
                    <div style={{ fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                        TOTAL USERS: {users.length}
                    </div>
                </div>

                <div style={{ overflowX: 'auto' }}>
                    <table className="session-table" style={{ width: '100%', borderCollapse: 'collapse' }}>
                        <thead>
                            <tr style={{ textAlign: 'left', background: '#f8fafc', borderBottom: '1px solid #e2e8f0', color: 'var(--color-text-muted)', fontSize: '11px' }}>
                                <th style={{ padding: '12px 24px' }}>NAME</th>
                                <th style={{ padding: '12px 24px' }}>ROLE</th>
                                <th style={{ padding: '12px 24px' }}>STATUS</th>
                                <th style={{ padding: '12px 24px' }}>JOINED</th>
                                <th style={{ padding: '12px 24px', textAlign: 'right' }}>ACTIONS</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredUsers.map(user => (
                                <tr key={user.id} style={{ borderBottom: '1px solid #f1f5f9', fontSize: '13px' }}>
                                    <td style={{ padding: '16px 24px' }}>
                                        <div style={{ fontWeight: 700, color: 'var(--color-text-primary)' }}>{user.name}</div>
                                        <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', display: 'flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}>
                                            <Mail size={10} /> {user.email}
                                        </div>
                                    </td>
                                    <td style={{ padding: '16px 24px' }}>
                                        <span style={{ fontSize: '11px', fontWeight: 700, background: '#f1f5f9', padding: '4px 8px', borderRadius: '4px' }}>
                                            {user.role?.replace('ROLE_', '')}
                                        </span>
                                    </td>
                                    <td style={{ padding: '16px 24px' }}>
                                        <span className={`status-badge status-badge--${user.status?.toLowerCase()}`} style={{ fontSize: '11px' }}>
                                            {user.status}
                                        </span>
                                    </td>
                                    <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: '12px' }}>
                                        {new Date(user.createdAt).toLocaleDateString()}
                                    </td>
                                    <td style={{ padding: '16px 24px', textAlign: 'right' }}>
                                        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
                                            {user.status === 'PENDING' && (
                                                <button onClick={() => handleApprove(user.id)} title="Approve" style={{ color: '#10b981', padding: '6px', borderRadius: '6px', border: '1px solid #d1fae5' }}><CheckCircle size={16} /></button>
                                            )}
                                            {user.status !== 'REJECTED' && (
                                                <button onClick={() => handleSuspend(user.id)} title="Suspend" style={{ color: '#f59e0b', padding: '6px', borderRadius: '6px', border: '1px solid #fef3c7' }}><XCircle size={16} /></button>
                                            )}
                                            <button onClick={() => handleDelete(user.id)} title="Delete Permanently" style={{ color: '#ef4444', padding: '6px', borderRadius: '6px', border: '1px solid #fee2e2' }}><Trash2 size={16} /></button>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </article>
        </AdminLayout>
    );
}
