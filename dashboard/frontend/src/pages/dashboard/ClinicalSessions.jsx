import { useState } from 'react';
import ClinicianSidebar from '../../components/dashboard/ClinicianSidebar';

const MOCK_SESSIONS = [
    { id: 1, student: 'Alex Johnson', date: 'Today', duration: '32 min', status: 'Completed', intervention: 'Breathing Exercise' },
    { id: 2, student: 'Emma Smith', date: 'Yesterday', duration: '28 min', status: 'Completed', intervention: 'Gentle Prompt' },
    { id: 3, student: 'Liam Brown', date: 'Yesterday', duration: '45 min', status: 'Completed', intervention: 'Visual Schedule' },
    { id: 4, student: 'Sophia Davis', date: '2 days ago', duration: '20 min', status: 'Incomplete', intervention: 'Token Board' },
    { id: 5, student: 'Noah Wilson', date: '2 days ago', duration: '35 min', status: 'Completed', intervention: 'Social Story' },
    { id: 6, student: 'Olivia Martinez', date: '3 days ago', duration: '40 min', status: 'Completed', intervention: 'Breathing Exercise' },
    { id: 7, student: 'Alex Johnson', date: '3 days ago', duration: '30 min', status: 'Incomplete', intervention: 'Gentle Prompt' },
    { id: 8, student: 'Emma Smith', date: '4 days ago', duration: '25 min', status: 'Completed', intervention: 'Visual Schedule' },
];

const STATUS_COLORS = {
    Completed: { bg: '#ecfdf5', text: '#059669' },
    Incomplete: { bg: '#fef2f2', text: '#dc2626' },
};

const STUDENTS = ['All Students', ...new Set(MOCK_SESSIONS.map(s => s.student))];
const DATE_OPTIONS = ['All Dates', 'Today', 'Yesterday', '2 days ago', '3 days ago', '4 days ago'];
const STATUS_OPTIONS = ['All Statuses', 'Completed', 'Incomplete'];

export default function ClinicalSessions() {
    const [filterStudent, setFilterStudent] = useState('All Students');
    const [filterDate, setFilterDate] = useState('All Dates');
    const [filterStatus, setFilterStatus] = useState('All Statuses');

    const filtered = MOCK_SESSIONS.filter(s => {
        if (filterStudent !== 'All Students' && s.student !== filterStudent) return false;
        if (filterDate !== 'All Dates' && s.date !== filterDate) return false;
        if (filterStatus !== 'All Statuses' && s.status !== filterStatus) return false;
        return true;
    });

    return (
        <div className="dashboard-layout" style={{ background: 'var(--color-bg)', minHeight: '100vh', display: 'flex' }}>
            <ClinicianSidebar />

            <main className="dashboard-main" style={{ padding: '40px', width: '100%', flex: 1, overflowY: 'auto' }}>
                <div style={{ marginBottom: 32 }}>
                    <h1 style={{ fontSize: 28, color: 'var(--color-text-primary)', margin: '0 0 8px 0' }}>Sessions</h1>
                    <p style={{ color: 'var(--color-text-muted)', margin: 0, fontSize: 16 }}>
                        Review all therapy sessions across your students.
                    </p>
                </div>

                {/* Filters */}
                <div style={{ display: 'flex', gap: 16, marginBottom: 28, flexWrap: 'wrap' }}>
                    <FilterSelect
                        label="Date Range"
                        value={filterDate}
                        options={DATE_OPTIONS}
                        onChange={setFilterDate}
                    />
                    <FilterSelect
                        label="Student"
                        value={filterStudent}
                        options={STUDENTS}
                        onChange={setFilterStudent}
                    />
                    <FilterSelect
                        label="Session Status"
                        value={filterStatus}
                        options={STATUS_OPTIONS}
                        onChange={setFilterStatus}
                    />
                    {(filterStudent !== 'All Students' || filterDate !== 'All Dates' || filterStatus !== 'All Statuses') && (
                        <button
                            onClick={() => {
                                setFilterStudent('All Students');
                                setFilterDate('All Dates');
                                setFilterStatus('All Statuses');
                            }}
                            style={{
                                alignSelf: 'flex-end', padding: '8px 16px', borderRadius: 8,
                                border: '1px solid var(--color-border)', background: 'transparent',
                                color: 'var(--color-text-muted)', cursor: 'pointer', fontSize: 13
                            }}
                        >
                            Clear Filters
                        </button>
                    )}
                </div>

                {/* Sessions Table */}
                <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
                    <div style={{
                        padding: '18px 24px',
                        borderBottom: '1px solid var(--color-border)',
                        background: '#fafafa',
                        display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                    }}>
                        <h2 style={{ fontSize: 17, margin: 0, color: 'var(--color-text-primary)' }}>Session Log</h2>
                        <span style={{ fontSize: 13, color: 'var(--color-text-muted)' }}>
                            {filtered.length} session{filtered.length !== 1 ? 's' : ''}
                        </span>
                    </div>

                    <div style={{ overflowX: 'auto' }}>
                        <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                            <thead>
                                <tr style={{
                                    borderBottom: '1px solid var(--color-border)',
                                    color: 'var(--color-text-muted)', fontSize: 12,
                                    textTransform: 'uppercase', letterSpacing: '0.06em'
                                }}>
                                    {['Student', 'Session Date', 'Duration', 'Status', 'Intervention Used'].map(col => (
                                        <th key={col} style={{ padding: '14px 24px', fontWeight: 600 }}>{col}</th>
                                    ))}
                                </tr>
                            </thead>
                            <tbody>
                                {filtered.length === 0 ? (
                                    <tr>
                                        <td colSpan={5} style={{ padding: '40px 24px', textAlign: 'center', color: 'var(--color-text-muted)', fontSize: 14 }}>
                                            No sessions match the selected filters.
                                        </td>
                                    </tr>
                                ) : (
                                    filtered.map(session => {
                                        const sc = STATUS_COLORS[session.status] || { bg: '#f1f5f9', text: '#475569' };
                                        return (
                                            <tr
                                                key={session.id}
                                                style={{
                                                    borderBottom: '1px solid var(--color-border)',
                                                    transition: 'background-color 0.15s'
                                                }}
                                                onMouseOver={e => e.currentTarget.style.backgroundColor = '#f8fafc'}
                                                onMouseOut={e => e.currentTarget.style.backgroundColor = 'transparent'}
                                            >
                                                {/* Student */}
                                                <td style={{ padding: '16px 24px', fontWeight: 500, color: 'var(--color-text-primary)' }}>
                                                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                                                        <div style={{
                                                            width: 30, height: 30, borderRadius: '50%',
                                                            background: 'linear-gradient(135deg, #e0f2fe 0%, #bae6fd 100%)',
                                                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                                                            color: '#0369a1', fontWeight: 700, fontSize: 13
                                                        }}>
                                                            {session.student.charAt(0)}
                                                        </div>
                                                        {session.student}
                                                    </div>
                                                </td>
                                                {/* Date */}
                                                <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>
                                                    {session.date}
                                                </td>
                                                {/* Duration */}
                                                <td style={{ padding: '16px 24px', color: 'var(--color-text-muted)', fontSize: 14 }}>
                                                    {session.duration}
                                                </td>
                                                {/* Status */}
                                                <td style={{ padding: '16px 24px' }}>
                                                    <span style={{
                                                        background: sc.bg, color: sc.text,
                                                        padding: '4px 10px', borderRadius: 12,
                                                        fontSize: 12, fontWeight: 600
                                                    }}>
                                                        {session.status}
                                                    </span>
                                                </td>
                                                {/* Intervention */}
                                                <td style={{ padding: '16px 24px', color: 'var(--color-text-primary)', fontSize: 14 }}>
                                                    {session.intervention}
                                                </td>
                                            </tr>
                                        );
                                    })
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </main>
        </div>
    );
}

function FilterSelect({ label, value, options, onChange }) {
    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            <label style={{ fontSize: 12, color: 'var(--color-text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {label}
            </label>
            <select
                value={value}
                onChange={e => onChange(e.target.value)}
                style={{
                    padding: '8px 32px 8px 14px', borderRadius: 8,
                    border: '1px solid var(--color-border)', fontSize: 14,
                    background: 'var(--color-surface)', color: 'var(--color-text-primary)',
                    cursor: 'pointer', outline: 'none', minWidth: 170,
                    appearance: 'none',
                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%2394a3b8' stroke-width='2'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E")`,
                    backgroundRepeat: 'no-repeat', backgroundPosition: 'right 10px center'
                }}
            >
                {options.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
        </div>
    );
}
