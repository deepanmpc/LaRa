import { useState, useEffect } from 'react';
import api from '../../services/api';

export default function AddChildModal({ isOpen, onClose, onAdd, childToEdit = null }) {
    const [formData, setFormData] = useState({ name: '', age: '', gradeLevel: '', clinicianId: '', diagnosis: '', notes: '', weeklySessionGoal: '5' });
    const [clinicians, setClinicians] = useState([]);
    const [searchTerm, setSearchTerm] = useState('');
    const [cliniciansLoading, setCliniciansLoading] = useState(false);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!isOpen) return;
        
        // Reset or populate form data
        if (childToEdit) {
            setFormData({
                name: childToEdit.name || '',
                age: childToEdit.age?.toString() || '',
                gradeLevel: childToEdit.gradeLevel || '',
                clinicianId: childToEdit.clinicianId?.toString() || '',
                diagnosis: childToEdit.diagnosis || '',
                notes: childToEdit.notes || '',
                weeklySessionGoal: childToEdit.weeklySessionGoal?.toString() || '5'
            });
        } else {
            setFormData({ name: '', age: '', gradeLevel: '', clinicianId: '', diagnosis: '', notes: '', weeklySessionGoal: '5' });
        }

        setCliniciansLoading(true);
        api.get('/clinician/approved')
            .then(res => setClinicians(res.data))
            .catch(() => setClinicians([]))
            .finally(() => setCliniciansLoading(false));
    }, [isOpen, childToEdit]);

    if (!isOpen) return null;

    const filteredClinicians = clinicians.filter(c => {
        const search = searchTerm.toLowerCase();
        return c.name.toLowerCase().includes(search) || 
               (c.organization && c.organization.toLowerCase().includes(search)) ||
               (c.specialization && c.specialization.toLowerCase().includes(search));
    });

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            await onAdd({
                id: childToEdit?.id, // Include ID if editing
                name: formData.name,
                age: parseInt(formData.age, 10),
                gradeLevel: formData.gradeLevel,
                clinicianId: formData.clinicianId ? parseInt(formData.clinicianId, 10) : null,
                diagnosis: formData.diagnosis || null,
                notes: formData.notes || null,
                weeklySessionGoal: parseInt(formData.weeklySessionGoal, 10) || 5
            });
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
            <div className="card" style={{ width: '100%', maxWidth: 480, margin: 20, maxHeight: '90vh', overflowY: 'auto' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 }}>
                    <h2 style={{ fontSize: 20, margin: 0, color: 'var(--color-text-primary)' }}>
                        {childToEdit ? 'Edit Child Profile' : 'Add Child'}
                    </h2>
                    <button onClick={onClose} style={{ background: 'none', border: 'none', fontSize: 24, cursor: 'pointer', color: 'var(--color-text-muted)' }}>&times;</button>
                </div>
                <form onSubmit={handleSubmit}>
                    <div className="form-group">
                        <label className="form-label">Child Name *</label>
                        <input type="text" className="form-input" required value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })} placeholder="e.g. Emma" />
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                        <div className="form-group">
                            <label className="form-label">Age *</label>
                            <input type="number" className="form-input" required min="1" max="18" value={formData.age} onChange={(e) => setFormData({ ...formData, age: e.target.value })} placeholder="e.g. 7" />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Grade Level *</label>
                            <input type="text" className="form-input" required value={formData.gradeLevel} onChange={(e) => setFormData({ ...formData, gradeLevel: e.target.value })} placeholder="e.g. 2nd Grade" />
                        </div>
                    </div>
                    <div className="form-group">
                        <label className="form-label">Diagnosis</label>
                        <input type="text" className="form-input" value={formData.diagnosis} onChange={(e) => setFormData({ ...formData, diagnosis: e.target.value })} placeholder="e.g. ASD Level 1, ADHD" />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Weekly Session Goal</label>
                        <input type="number" className="form-input" min="1" max="14" value={formData.weeklySessionGoal} onChange={(e) => setFormData({ ...formData, weeklySessionGoal: e.target.value })} placeholder="5" />
                    </div>
                    <div className="form-group">
                        <label className="form-label">Notes</label>
                        <textarea className="form-input" rows={3} value={formData.notes} onChange={(e) => setFormData({ ...formData, notes: e.target.value })} placeholder="Any notes about the child..." style={{ resize: 'vertical' }} />
                    </div>
                    <div className="form-group" style={{ position: 'relative' }}>
                        <label className="form-label">Assign Clinician (recommended for detailed dashboard)</label>
                        <div style={{ position: 'relative', marginBottom: 4 }}>
                            <input 
                                type="text" 
                                className="form-input" 
                                style={{ paddingLeft: 36, fontSize: 13, background: 'var(--color-bg)' }} 
                                placeholder="Search clinician by name or org..." 
                                value={searchTerm}
                                onChange={(e) => setSearchTerm(e.target.value)}
                                onFocus={() => setCliniciansLoading(false)} // Just to trigger re-render if needed
                            />
                            <svg style={{ position: 'absolute', left: 12, top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                            </svg>
                            {searchTerm && (
                                <button 
                                    type="button"
                                    onClick={() => setSearchTerm('')}
                                    style={{ position: 'absolute', right: 10, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', color: 'var(--color-text-muted)', cursor: 'pointer', padding: 4 }}
                                >
                                    &times;
                                </button>
                            )}
                        </div>

                        {/* Custom Dropdown List */}
                        <div style={{ 
                            maxHeight: 200, 
                            overflowY: 'auto', 
                            border: '1px solid var(--color-border)', 
                            borderRadius: 8, 
                            background: 'white',
                            boxShadow: searchTerm ? '0 4px 12px rgba(0,0,0,0.08)' : 'none',
                            display: (searchTerm || formData.clinicianId) ? 'block' : 'none',
                            marginTop: 4
                        }}>
                            {cliniciansLoading ? (
                                <div style={{ padding: '12px', fontSize: 13, color: 'var(--color-text-muted)', textAlign: 'center' }}>Loading clinicians...</div>
                            ) : (
                                <>
                                    <div 
                                        onClick={() => {
                                            setFormData({ ...formData, clinicianId: '' });
                                            setSearchTerm('');
                                        }}
                                        style={{ 
                                            padding: '10px 12px', 
                                            fontSize: 13, 
                                            cursor: 'pointer', 
                                            background: !formData.clinicianId ? 'var(--color-bg)' : 'transparent',
                                            borderBottom: '1px solid var(--color-border)',
                                            color: !formData.clinicianId ? 'var(--color-primary)' : 'var(--color-text-primary)',
                                            fontWeight: !formData.clinicianId ? 600 : 400
                                        }}
                                    >
                                        — No clinician assigned —
                                    </div>
                                    {filteredClinicians
                                        .sort((a, b) => a.name.localeCompare(b.name))
                                        .map(c => {
                                            const isSelected = formData.clinicianId === c.id.toString();
                                            return (
                                                <div 
                                                    key={c.id} 
                                                    onClick={() => {
                                                        setFormData({ ...formData, clinicianId: c.id.toString() });
                                                        setSearchTerm(c.name);
                                                    }}
                                                    style={{ 
                                                        padding: '10px 12px', 
                                                        fontSize: 13, 
                                                        cursor: 'pointer', 
                                                        transition: 'background 0.2s',
                                                        background: isSelected ? 'rgba(124, 58, 237, 0.05)' : 'transparent',
                                                        borderBottom: '1px solid var(--color-border)',
                                                        display: 'flex',
                                                        justifyContent: 'space-between',
                                                        alignItems: 'center'
                                                    }}
                                                    onMouseEnter={(e) => e.currentTarget.style.background = 'var(--color-bg)'}
                                                    onMouseLeave={(e) => e.currentTarget.style.background = isSelected ? 'rgba(124, 58, 237, 0.05)' : 'transparent'}
                                                >
                                                    <div>
                                                        <div style={{ fontWeight: isSelected ? 600 : 500, color: isSelected ? 'var(--color-primary)' : 'var(--color-text-primary)' }}>{c.name}</div>
                                                        <div style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>
                                                            {c.organization ? c.organization : 'Private Practice'} {c.specialization ? ` · ${c.specialization}` : ''}
                                                        </div>
                                                    </div>
                                                    {isSelected && (
                                                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                                                            <polyline points="20 6 9 17 4 12" />
                                                        </svg>
                                                    )}
                                                </div>
                                            );
                                        })
                                    }
                                </>
                            )}
                            {searchTerm && filteredClinicians.length === 0 && !cliniciansLoading && (
                                <div style={{ padding: '12px', fontSize: 12, color: 'var(--color-text-muted)', textAlign: 'center' }}>
                                    No clinicians match "{searchTerm}"
                                </div>
                            )}
                        </div>
                        {clinicians.length === 0 && !cliniciansLoading && (
                            <div style={{ fontSize: 12, color: 'var(--color-text-muted)', marginTop: 4 }}>
                                No approved clinicians available yet.
                            </div>
                        )}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'flex-end', gap: 12, marginTop: 24 }}>
                        <button type="button" onClick={onClose} className="btn-secondary" style={{ padding: '8px 16px', borderRadius: 8, border: '1px solid var(--color-border)', background: 'white', cursor: 'pointer', color: 'var(--color-text-primary)' }}>Cancel</button>
                        <button type="submit" className="btn-primary" disabled={loading} style={{ padding: '8px 16px', borderRadius: 8 }}>
                            {loading ? 'Saving...' : (childToEdit ? 'Save Changes' : 'Add Child')}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
