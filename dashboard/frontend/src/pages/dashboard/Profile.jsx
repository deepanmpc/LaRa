import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { getStoredUser } from '../../services/authService';
import api from '../../services/api';
import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';

// Family profile sidebar uses the FamilyDashboard's Sidebar
import Sidebar from '../../components/Sidebar';

export default function Profile() {
    const navigate = useNavigate();
    const user = getStoredUser();
    const isClinician = user?.role === 'ROLE_CLINICIAN';
    const isFamily = user?.role === 'ROLE_FAMILY';

    const [showModal, setShowModal] = useState(false);
    const [form, setForm] = useState({
        name: user?.name || '',
        email: user?.email || '',
        organization: user?.organization || '',
        specialization: user?.specialization || '',
    });

    const roleLabel = isClinician ? 'Clinician' : isFamily ? 'Family' : user?.role || 'User';

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [profileData, setProfileData] = useState(user);

    const fetchProfile = async () => {
        try {
            setLoading(true);
            const response = await api.get('/users/profile');
            setProfileData(response.data);
            setForm({
                name: response.data.name || '',
                email: response.data.email || '',
                organization: response.data.organization || '',
                specialization: response.data.specialization || '',
            });
        } catch (err) {
            console.error('Failed to fetch profile', err);
            // Fallback to local storage user
            setProfileData(user);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchProfile();
    }, []);

    const handleInputChange = (e) => {
        setForm({ ...form, [e.target.name]: e.target.value });
    };

    const handleSave = async () => {
        try {
            setSaving(true);
            setError(null);
            
            await api.put('/users/profile', {
                name: form.name,
                email: form.email,
                organization: form.organization,
                specialization: form.specialization,
            });

            // Refresh live data and local storage fallback
            await fetchProfile();
            
            // Update local storage so if user refreshes it doesn't blink old data
            const currentUser = getStoredUser();
            localStorage.setItem('lara_user', JSON.stringify({
                ...currentUser,
                name: form.name,
                email: form.email
            }));

            setShowModal(false);
        } catch (err) {
            console.error('Failed to save profile', err);
            setError('Failed to update profile. Please try again.');
        } finally {
            setSaving(false);
        }
    };

    const profileContent = (
        <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, overflowY: 'auto' }}>
            <div style={{ marginBottom: 32 }}>
                <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>My Profile</h1>
                <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 16 }}>
                    View and manage your account information.
                </p>
            </div>

            {/* Profile Info Card */}
            <div style={{ display: 'grid', gridTemplateColumns: isClinician ? '1fr 1fr' : '1fr', gap: 24, marginBottom: 24, maxWidth: 900 }}>

                {/* User Info Card */}
                <div className="card" style={{ padding: '28px 32px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 18, marginBottom: 24 }}>
                        <div style={{
                            width: 64, height: 64, borderRadius: '50%',
                            background: 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            color: '#0369a1', fontWeight: 700, fontSize: 26
                        }}>
                            {profileData?.name?.charAt(0)?.toUpperCase() || '?'}
                        </div>
                        <div>
                            <div style={{ fontSize: 20, fontWeight: 700, color: 'var(--color-text-primary)' }}>{profileData?.name || '—'}</div>
                            <div style={{
                                display: 'inline-block', marginTop: 6,
                                background: isClinician ? '#e0f2fe' : '#f0fdf4',
                                color: isClinician ? '#0369a1' : '#16a34a',
                                fontSize: 12, fontWeight: 600,
                                padding: '3px 10px', borderRadius: 999
                            }}>{roleLabel}</div>
                        </div>
                    </div>

                    <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 20 }}>
                        <h3 style={{ fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--color-text-muted)', margin: '0 0 16px 0' }}>
                            Profile Information
                        </h3>

                        <ProfileField label="Name" value={profileData?.name} />
                        <ProfileField label="Email" value={profileData?.email} />
                        <ProfileField label="Role" value={roleLabel} />
                    </div>

                    <button
                        className="btn-primary"
                        style={{ marginTop: 24, padding: '10px 20px', fontSize: 14 }}
                        onClick={() => setShowModal(true)}
                    >
                        Edit Profile
                    </button>
                </div>

                {/* Clinician-specific fields */}
                {isClinician && (
                    <div className="card" style={{ padding: '28px 32px' }}>
                        <h3 style={{ fontSize: 13, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--color-text-muted)', margin: '0 0 20px 0' }}>
                            Clinician Details
                        </h3>
                        <ProfileField label="Organization" value={profileData?.organization || '—'} />
                        <ProfileField label="License ID" value={profileData?.licenseNumber || '—'} />
                        <ProfileField label="Specialization" value={profileData?.specialization || '—'} />
                    </div>
                )}
            </div>

            {/* Edit Profile Modal */}
            {showModal && (
                <div style={{
                    position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.4)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000
                }}>
                    <div className="card" style={{
                        width: '100%', maxWidth: 480, padding: '32px', position: 'relative',
                        boxShadow: '0 20px 60px rgba(0,0,0,0.15)'
                    }}>
                        {/* Close button */}
                        <button
                            onClick={() => setShowModal(false)}
                            style={{
                                position: 'absolute', top: 16, right: 16,
                                background: 'none', border: 'none', cursor: 'pointer',
                                color: 'var(--color-text-muted)', fontSize: 20, lineHeight: 1
                            }}
                        >
                            ✕
                        </button>

                        <h2 style={{ fontSize: 20, color: 'var(--color-text-primary)', margin: '0 0 24px 0' }}>
                            Edit Profile
                        </h2>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                            <ModalField label="Name" name="name" value={form.name} onChange={handleInputChange} />
                            <ModalField label="Email" name="email" value={form.email} onChange={handleInputChange} type="email" />
                            {isClinician && (
                                <>
                                    <ModalField label="Organization" name="organization" value={form.organization} onChange={handleInputChange} />
                                    <ModalField label="Specialization" name="specialization" value={form.specialization} onChange={handleInputChange} />
                                </>
                            )}
                        </div>

                        <div style={{ display: 'flex', gap: 12, marginTop: 28, justifyContent: 'flex-end', alignItems: 'center' }}>
                            {error && <span style={{ color: '#dc2626', fontSize: 13, marginRight: 'auto' }}>{error}</span>}
                            <button
                                onClick={() => setShowModal(false)}
                                disabled={saving}
                                style={{
                                    padding: '10px 20px', border: '1px solid var(--color-border)',
                                    borderRadius: 8, background: 'transparent',
                                    color: 'var(--color-text-muted)', cursor: saving ? 'not-allowed' : 'pointer', fontSize: 14,
                                    opacity: saving ? 0.6 : 1
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleSave}
                                disabled={saving}
                                style={{
                                    padding: '10px 20px', borderRadius: 8, fontSize: 14,
                                    background: 'var(--color-primary)', color: '#fff', border: 'none',
                                    cursor: saving ? 'not-allowed' : 'pointer',
                                    display: 'flex', alignItems: 'center', gap: 8,
                                    opacity: saving ? 0.8 : 1
                                }}
                            >
                                {saving ? (
                                    <>
                                        <svg className="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                            <line x1="12" y1="2" x2="12" y2="6"></line>
                                            <line x1="12" y1="18" x2="12" y2="22"></line>
                                            <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                                            <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                                            <line x1="2" y1="12" x2="6" y2="12"></line>
                                            <line x1="18" y1="12" x2="22" y2="12"></line>
                                            <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                                            <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
                                        </svg>
                                        Saving...
                                    </>
                                ) : 'Save Changes'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            {isClinician ? (
                <ClinicianSidebar activeOverride="profile" />
            ) : (
                <Sidebar activeItem="profile" onNavClick={(id) => {
                    if (id === 'summary') navigate('/dashboard/children');
                }} />
            )}
            {profileContent}
        </div>
    );
}

function ProfileField({ label, value }) {
    return (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: 14, marginBottom: 14, borderBottom: '1px solid var(--color-border)' }}>
            <span style={{ fontSize: 13, color: 'var(--color-text-muted)', fontWeight: 500 }}>{label}</span>
            <span style={{ fontSize: 14, color: 'var(--color-text-primary)', fontWeight: 600 }}>{value || '—'}</span>
        </div>
    );
}

function ModalField({ label, name, value, onChange, type = 'text' }) {
    return (
        <div>
            <label style={{ fontSize: 13, color: 'var(--color-text-muted)', fontWeight: 500, display: 'block', marginBottom: 6 }}>
                {label}
            </label>
            <input
                type={type}
                name={name}
                value={value}
                onChange={onChange}
                style={{
                    width: '100%', padding: '10px 14px', borderRadius: 8,
                    border: '1px solid var(--color-border)', fontSize: 14,
                    color: 'var(--color-text-primary)', background: 'var(--color-bg)',
                    outline: 'none', boxSizing: 'border-box'
                }}
            />
        </div>
    );
}
