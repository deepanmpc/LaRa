import { useState, useEffect } from 'react';
import AdminLayout from '../../components/dashboard/AdminLayout';
import { UserCheck, XCircle, CheckCircle } from 'lucide-react';
import api from '../../services/api';

export default function AdminClinicians() {
    const [clinicians, setClinicians] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchClinicians = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('lara_token');
            const res = await fetch('/api/admin/clinicians/pending', {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            if (!res.ok) {
                throw new Error("API failed: " + res.status);
            }

            const data = await res.json();
            setClinicians(Array.isArray(data) ? data : []);

        } catch (err) {
            console.error("FETCH ERROR:", err);
            setError(err.message || 'Failed to fetch pending clinicians.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClinicians();
    }, []);

    const handleApprove = async (id) => {
        try {
            const token = localStorage.getItem('lara_token');
            const res = await fetch(`/api/admin/clinicians/${id}/approve`, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            if (!res.ok) {
                throw new Error("Failed to approve");
            }

            setClinicians(prev => prev.filter(c => c.id !== id));
            console.log(`Clinician ${id} approved successfully`);
        } catch (err) {
            console.error(`Failed to approve clinician ${id}`, err);
        }
    };

    const handleReject = async (id) => {
        try {
            const token = localStorage.getItem('lara_token');
            const res = await fetch(`/api/admin/clinicians/${id}/reject`, {
                method: 'POST',
                headers: {
                    Authorization: `Bearer ${token}`
                }
            });

            if (!res.ok) {
                throw new Error("Failed to reject");
            }

            setClinicians(prev => prev.filter(c => c.id !== id));
            console.log(`Clinician ${id} rejected successfully`);
        } catch (err) {
            console.error(`Failed to reject clinician ${id}`, err);
        }
    };

    return (
        <AdminLayout 
            title="Clinician Approvals" 
            subtitle="Manage pending clinician registrations."
        >
            <div className="clinical-panel">
                <div className="clinical-panel__header">
                    <h3 className="clinical-panel__title" style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <UserCheck size={18} />
                        Pending Approvals
                    </h3>
                </div>

                <div className="clinical-table-container">
                    {loading ? (
                        <div style={{ padding: '32px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                            Loading clinicians...
                        </div>
                    ) : error ? (
                        <div style={{ padding: '32px', textAlign: 'center' }}>
                            <p style={{ color: 'var(--color-risk)' }}>{error}</p>
                            <button className="clinical-btn clinical-btn--primary" onClick={fetchClinicians} style={{ marginTop: '16px' }}>
                                Retry
                            </button>
                        </div>
                    ) : clinicians.length === 0 ? (
                        <div style={{ padding: '32px', textAlign: 'center', color: 'var(--color-text-muted)' }}>
                            No pending approvals
                        </div>
                    ) : (
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                                <thead>
                                    <tr style={{ background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
                                        <th style={{ padding: '12px 24px', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-muted)' }}>Practitioner</th>
                                        <th style={{ padding: '12px 24px', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-muted)' }}>Contact Info</th>
                                        <th style={{ padding: '12px 24px', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-muted)' }}>Applied on</th>
                                        <th style={{ padding: '12px 24px', fontSize: '13px', fontWeight: 600, color: 'var(--color-text-muted)' }}>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {clinicians.map((clinician, index) => {
                                        const initials = clinician.name ? clinician.name.substring(0, 2).toUpperCase() : 'DR';
                                        const formattedDate = clinician.createdAt 
                                            ? new Date(clinician.createdAt).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
                                            : 'N/A';

                                        return (
                                            <tr key={clinician.id} style={{ borderBottom: index === clinicians.length - 1 ? 'none' : '1px solid #f1f5f9', transition: 'background 0.2s' }}>
                                                <td style={{ padding: '16px 24px' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                                        <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: '#e0f2fe', color: '#0369a1', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700, fontSize: '14px' }}>
                                                            {initials}
                                                        </div>
                                                        <div>
                                                            <div style={{ fontWeight: 600, fontSize: '15px', color: 'var(--color-text-primary)' }}>{clinician.name}</div>
                                                            <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '2px' }}>ID: {clinician.id}</div>
                                                        </div>
                                                    </div>
                                                </td>
                                                <td style={{ padding: '16px 24px' }}>
                                                    <div style={{ fontSize: '14px', color: 'var(--color-text-primary)' }}>{clinician.email}</div>
                                                    <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '2px' }}>Pending Verification</div>
                                                </td>
                                                <td style={{ padding: '16px 24px', fontSize: '14px', color: 'var(--color-text-primary)' }}>
                                                    <div style={{ display: 'inline-flex', padding: '4px 10px', background: '#f8fafc', border: '1px solid #e2e8f0', borderRadius: '16px', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)' }}>
                                                        {formattedDate}
                                                    </div>
                                                </td>
                                                <td style={{ padding: '16px 24px' }}>
                                                    <div style={{ display: 'flex', gap: '10px' }}>
                                                        <button 
                                                            onClick={() => handleApprove(clinician.id)}
                                                            title="Approve"
                                                            style={{ 
                                                                background: '#d1fae5', border: 'none', cursor: 'pointer', 
                                                                color: '#065f46', display: 'flex', alignItems: 'center', gap: '6px',
                                                                padding: '6px 12px', borderRadius: '6px', fontWeight: 600, fontSize: '13px',
                                                                transition: 'all 0.15s ease'
                                                            }}
                                                            onMouseOver={(e) => e.currentTarget.style.background = '#a7f3d0'}
                                                            onMouseOut={(e) => e.currentTarget.style.background = '#d1fae5'}
                                                        >
                                                            <CheckCircle size={16} /> Approve
                                                        </button>
                                                        <button 
                                                            onClick={() => handleReject(clinician.id)}
                                                            title="Reject"
                                                            style={{ 
                                                                background: '#fee2e2', border: 'none', cursor: 'pointer', 
                                                                color: '#991b1b', display: 'flex', alignItems: 'center', gap: '6px',
                                                                padding: '6px 12px', borderRadius: '6px', fontWeight: 600, fontSize: '13px',
                                                                transition: 'all 0.15s ease'
                                                            }}
                                                            onMouseOver={(e) => e.currentTarget.style.background = '#fecaca'}
                                                            onMouseOut={(e) => e.currentTarget.style.background = '#fee2e2'}
                                                        >
                                                            <XCircle size={16} /> Reject
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </AdminLayout>
    );
}
