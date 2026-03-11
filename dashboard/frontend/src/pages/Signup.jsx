import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { register } from '../services/authService';

export default function Signup() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: 'ROLE_FAMILY',
        phone: '',
        organization: '',
        licenseNumber: '',
        specialization: '',
        yearsOfExperience: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const isClinicianRole = formData.role === 'ROLE_CLINICIAN';

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (formData.password.length < 6) {
            setError('Password must be at least 6 characters');
            return;
        }

        setLoading(true);
        try {
            const payload = {
                name: formData.name,
                email: formData.email,
                password: formData.password,
                role: formData.role,
                ...(isClinicianRole && {
                    phone: formData.phone,
                    organization: formData.organization,
                    licenseNumber: formData.licenseNumber,
                    specialization: formData.specialization,
                    yearsOfExperience: formData.yearsOfExperience ? parseInt(formData.yearsOfExperience) : null,
                }),
            };

            const data = await register(payload);

            if (data.role === 'ROLE_FAMILY') {
                navigate('/dashboard/children');
            } else if (data.role === 'ROLE_CLINICIAN') {
                navigate('/clinician/pending');
            }
        } catch (err) {
            setError(err.response?.data?.error || 'Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-card" style={{ maxWidth: 500 }}>
                <div className="auth-logo">
                    <div className="auth-logo-icon">L</div>
                    <div className="auth-logo-text">La<span>Ra</span> Care</div>
                </div>
                <h1 className="auth-title">Create your account</h1>
                <p className="auth-subtitle">Join the LaRa Care platform today</p>

                {error && <div className="error-message">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label" htmlFor="signup-name">Full Name</label>
                        <input
                            id="signup-name"
                            name="name"
                            type="text"
                            className="form-input"
                            placeholder="Alex Johnson"
                            value={formData.name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="signup-email">Email Address</label>
                        <input
                            id="signup-email"
                            name="email"
                            type="email"
                            className="form-input"
                            placeholder="you@example.com"
                            value={formData.email}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="signup-role">I am registering as</label>
                        <select
                            id="signup-role"
                            name="role"
                            className="form-select"
                            value={formData.role}
                            onChange={handleChange}
                        >
                            <option value="ROLE_FAMILY">Family Member / Parent</option>
                            <option value="ROLE_CLINICIAN">Clinician / Therapist</option>
                        </select>
                    </div>

                    {isClinicianRole && (
                        <>
                            <div style={{
                                background: '#f0f9ff',
                                border: '1px solid #bae6fd',
                                borderRadius: 12,
                                padding: '14px 16px',
                                marginBottom: 20,
                                fontSize: 13,
                                color: '#0369a1'
                            }}>
                                ℹ️ Clinician accounts require admin approval before activation.
                            </div>
                            <div className="form-group">
                                <label className="form-label" htmlFor="signup-phone">Phone Number</label>
                                <input
                                    id="signup-phone"
                                    name="phone"
                                    type="tel"
                                    className="form-input"
                                    placeholder="e.g. 555-123-4567"
                                    value={formData.phone}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label" htmlFor="signup-organization">Organization / Clinic</label>
                                <input
                                    id="signup-organization"
                                    name="organization"
                                    type="text"
                                    className="form-input"
                                    placeholder="e.g. Mindful Care Center"
                                    value={formData.organization}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label" htmlFor="signup-license">License Number</label>
                                <input
                                    id="signup-license"
                                    name="licenseNumber"
                                    type="text"
                                    className="form-input"
                                    placeholder="e.g. BCBA-123456"
                                    value={formData.licenseNumber}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label" htmlFor="signup-specialization">Specialization</label>
                                <input
                                    id="signup-specialization"
                                    name="specialization"
                                    type="text"
                                    className="form-input"
                                    placeholder="e.g. Child Psychology, ABA Therapy"
                                    value={formData.specialization}
                                    onChange={handleChange}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label" htmlFor="signup-years">Years of Experience</label>
                                <input
                                    id="signup-years"
                                    name="yearsOfExperience"
                                    type="number"
                                    className="form-input"
                                    placeholder="e.g. 5"
                                    value={formData.yearsOfExperience}
                                    onChange={handleChange}
                                    min="0"
                                    max="60"
                                />
                            </div>
                        </>
                    )}

                    <div className="form-group">
                        <label className="form-label" htmlFor="signup-password">Password</label>
                        <input
                            id="signup-password"
                            name="password"
                            type="password"
                            className="form-input"
                            placeholder="Minimum 6 characters"
                            value={formData.password}
                            onChange={handleChange}
                            required
                            minLength={6}
                        />
                    </div>

                    <div className="form-group">
                        <label className="form-label" htmlFor="signup-confirm">Confirm Password</label>
                        <input
                            id="signup-confirm"
                            name="confirmPassword"
                            type="password"
                            className="form-input"
                            placeholder="Repeat your password"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    <button
                        id="signup-submit-btn"
                        type="submit"
                        className="btn-primary"
                        disabled={loading}
                    >
                        {loading ? 'Creating account...' : 'Create Account'}
                    </button>
                </form>

                <div className="auth-divider">or</div>
                <div className="auth-link">
                    Already have an account? <Link to="/login">Sign in</Link>
                </div>
            </div>
        </div>
    );
}
