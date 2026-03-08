import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';

export default function ChildSwitcher({ currentChildId }) {
    const [children, setChildren] = useState([]);
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchChildren = async () => {
            try {
                const response = await api.get('/children');
                setChildren(response.data);
            } catch (err) {
                console.error('Failed to fetch children for switcher', err);
            }
        };
        fetchChildren();
    }, []);

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const activeChild = children.find(c => c.id === parseInt(currentChildId)) || children[0];

    if (!activeChild) return null; // Wait for load

    return (
        <div className="child-switcher" ref={dropdownRef} style={{ position: 'relative' }}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    display: 'flex', alignItems: 'center', gap: 10,
                    padding: '6px 16px 6px 6px',
                    background: 'var(--color-bg)',
                    border: '1px solid var(--color-border)',
                    borderRadius: 30,
                    cursor: 'pointer',
                    transition: 'all 0.2s'
                }}
                onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--color-primary)'}
                onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--color-border)'}
            >
                <div style={{
                    width: 32, height: 32, borderRadius: '50%',
                    background: 'var(--color-primary)', color: 'white',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontWeight: 600, fontSize: 14
                }}>
                    {activeChild.name.charAt(0)}
                </div>
                <div style={{ textAlign: 'left' }}>
                    <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--color-text-primary)' }}>{activeChild.name}</div>
                </div>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ marginLeft: 4, color: 'var(--color-text-muted)' }}>
                    <polyline points="6 9 12 15 18 9"></polyline>
                </svg>
            </button>

            {isOpen && (
                <div style={{
                    position: 'absolute', top: 'calc(100% + 8px)', left: 0,
                    background: 'white', borderRadius: 12,
                    boxShadow: '0 10px 25px -5px rgba(0,0,0,0.1), 0 8px 10px -6px rgba(0,0,0,0.1)',
                    border: '1px solid var(--color-border)',
                    width: 220, zIndex: 100, overflow: 'hidden'
                }}>
                    <div style={{ padding: '12px 14px', borderBottom: '1px solid var(--color-border)', fontSize: 11, fontWeight: 600, color: 'var(--color-text-muted)', textTransform: 'uppercase' }}>
                        Switch Child Profile
                    </div>
                    {children.map(child => (
                        <div
                            key={child.id}
                            onClick={() => {
                                setIsOpen(false);
                                if (child.id !== activeChild.id) {
                                    navigate(`/dashboard/family/${child.id}`);
                                }
                            }}
                            style={{
                                padding: '10px 14px', display: 'flex', alignItems: 'center', gap: 12,
                                cursor: 'pointer', transition: 'background 0.2s',
                                background: child.id === activeChild.id ? 'var(--color-bg)' : 'transparent'
                            }}
                            onMouseEnter={e => e.currentTarget.style.background = 'var(--color-bg)'}
                            onMouseLeave={e => e.currentTarget.style.background = child.id === activeChild.id ? 'var(--color-bg)' : 'transparent'}
                        >
                            <div style={{
                                width: 28, height: 28, borderRadius: '50%',
                                background: child.id === activeChild.id ? 'var(--color-primary)' : 'var(--color-border)',
                                color: child.id === activeChild.id ? 'white' : 'var(--color-text-primary)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                fontWeight: 500, fontSize: 12
                            }}>
                                {child.name.charAt(0)}
                            </div>
                            <div>
                                <div style={{ fontSize: 13, fontWeight: child.id === activeChild.id ? 600 : 500, color: 'var(--color-text-primary)' }}>{child.name}</div>
                                <div style={{ fontSize: 11, color: 'var(--color-text-muted)' }}>Age {child.age}</div>
                            </div>
                            {child.id === activeChild.id && (
                                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="var(--color-primary)" strokeWidth="2" style={{ marginLeft: 'auto' }}>
                                    <polyline points="20 6 9 17 4 12"></polyline>
                                </svg>
                            )}
                        </div>
                    ))}
                    <div
                        onClick={() => navigate('/dashboard/children')}
                        style={{
                            padding: '12px 14px', borderTop: '1px solid var(--color-border)',
                            display: 'flex', alignItems: 'center', gap: 8,
                            cursor: 'pointer', fontSize: 13, fontWeight: 500, color: 'var(--color-primary)'
                        }}
                        onMouseEnter={e => e.currentTarget.style.background = 'var(--color-bg)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                    >
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        Manage Children
                    </div>
                </div>
            )}
        </div>
    );
}
