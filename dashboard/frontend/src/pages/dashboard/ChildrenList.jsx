import { useState, useEffect } from 'react';

import api from '../../services/api';
import ChildCard from '../../components/dashboard/ChildCard';
import AddChildCard from '../../components/dashboard/AddChildCard';
import AddChildModal from '../../components/modals/AddChildModal';

export default function ChildrenList() {
    const [children, setChildren] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const fetchChildren = async () => {
        try {
            const response = await api.get('/children');
            setChildren(response.data);
        } catch (err) {
            console.error('Failed to fetch children APIs', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchChildren();
    }, []);

    const handleAddChild = async (childData) => {
        try {
            await api.post('/children', childData);
            await fetchChildren();
        } catch (err) {
            console.error('Failed to add child to database:', err);
            alert('Error: Could not save child to database. Please check if the backend is running.');
            throw err; // Propagate to modal to keep it open or show error
        }
    };

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <main className="dashboard-main" style={{ padding: '40px', maxWidth: 1000, margin: '0 auto', width: '100%' }}>
                <div style={{ marginBottom: 32 }}>
                    <div className="auth-logo" style={{ justifyContent: 'flex-start', marginBottom: 24, padding: 0 }}>
                        <div className="auth-logo-icon">L</div>
                        <div className="auth-logo-text">La<span>Ra</span> Care</div>
                    </div>
                    <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>Welcome back to LaRa Care</h1>
                    <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 16 }}>Select a profile to view the dashboard and start a session.</p>
                </div>

                {loading ? (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 24 }}>
                        <div className="card skeleton" style={{ height: 160 }}></div>
                        <div className="card skeleton" style={{ height: 160 }}></div>
                    </div>
                ) : (
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 24 }}>
                        {children.map(child => (
                            <ChildCard key={child.id} child={child} />
                        ))}
                        <AddChildCard onClick={() => setIsModalOpen(true)} />
                    </div>
                )}
            </main>

            <AddChildModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                onAdd={handleAddChild}
            />
        </div>
    );
}
