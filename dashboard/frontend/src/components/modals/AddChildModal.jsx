import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function AddChildModal({ isOpen, onClose, onAdd }) {
    const [formData, setFormData] = useState({ name: '', age: '', gradeLevel: '', clinicianId: '' });
    const [clinicians, setClinicians] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (isOpen) {
            const fetchClinicians = async () => {
                try {
                    const res = await api.get('/children/clinicians');
                    setClinicians(res.data);
                } catch (err) {
                    console.error('Failed to fetch clinicians', err);
                }
            };
            fetchClinicians();
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await onAdd({
                name: formData.name,
                age: parseInt(formData.age, 10),
                gradeLevel: formData.gradeLevel,
                clinicianId: formData.clinicianId ? parseInt(formData.clinicianId, 10) : null
            });
            setFormData({ name: '', age: '', gradeLevel: '', clinicianId: '' });
            onClose();
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
            background: 'rgba(0,0,0,0.5)', zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
            <div className="card" style={{ width: '100%', maxWidth: 400, margin: 20 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                    <h2 style={{ fontSize: 20, margin: 0, color: 'var(--color-text-primary)' }}>Add Child</h2>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 24, cursor: 'pointer', color: 'var(--color-text-muted)' }}>&times;</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Child Name</label>
                        <input type="text" className="form-input" required value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="e.g. Emma" />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Age</label>
                        <input type="number" className="form-input" required min="1" max="18" value={formData.age} onChange={(e) => setFormData({ ...formData, age: e.target.value })} placeholder="e.g. 7" />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Grade Level</label>
                        <input type="text" className="form-input" required value={formData.gradeLevel} onChange={(e) => setFormData({ ...formData, gradeLevel: e.target.value })} placeholder="e.g. 2nd Grade" />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Assign to Clinician</label>
                        <select 
                            className="form-input" 
                            required
                            value={formData.clinicianId} 
                            onChange={(e) => setFormData({ ...formData, clinicianId: e.target.value })}
                        >
                            <option value="">Select a Clinician</option>
                            {clinicians.map(c => (
                                <option key={c.id} value={c.id}>{c.name}</option>
                            ))}
                        </select>
                        <p style={{ fontSize: 11, color: 'var(--color-text-muted)', marginTop: 4 }}>
                            A clinician must be assigned to monitor progress and provide expert care.
                        </p>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
                        <button type="button" onClick={onClose} className="btn-secondary" style={{ padding: '8px 16px', borderRadius: 8, border: '1px solid var(--color-border)', background: 'white', cursor: 'pointer', color: 'var(--color-text-primary)' }}>Cancel</button>
                        <button type="submit" className="btn-primary" disabled={loading} style={{ padding: '8px 16px', borderRadius: 8 }}>
                            {loading ? 'Adding...' : 'Add Child'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
