import React from 'react';
import { Outlet, Navigate, NavLink } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { ShieldCheck, Target, LogOut, Activity, Database } from 'lucide-react';

const AdminLayout = () => {
    const { isAuthenticated, role, logout } = useAuthStore();

    // Route guard placeholder. Real prod would verify ROLE_ADMIN
    if (!isAuthenticated && process.env.NODE_ENV === 'production') {
        return <Navigate to="/login" replace />;
    }

    const navItems = [
        { path: '/admin/integrity', label: 'System Integrity', icon: <Target size={20} /> },
        { path: '/admin/logs', label: 'Audit Logs (WIP)', icon: <ShieldCheck size={20} /> },
        { path: '/admin/database', label: 'Database Health (WIP)', icon: <Database size={20} /> }
    ];

    return (
        <div className="flex h-screen bg-slate-900 text-slate-200">
            {/* Sidebar */}
            <aside className="w-64 bg-slate-950 border-r border-slate-800 flex flex-col">
                <div className="p-6 border-b border-slate-800 mb-4 flex items-center gap-3">
                    <ShieldCheck className="text-emerald-500" size={28} />
                    <h1 className="text-xl font-bold tracking-tight text-white">LaRa Admin</h1>
                </div>

                <nav className="flex-1 px-4 space-y-2">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                    ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                                }`
                            }
                        >
                            {item.icon}
                            <span className="font-medium text-sm">{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-slate-800">
                    <div className="px-4 py-3 bg-slate-900/50 rounded-lg mb-3 border border-slate-800">
                        <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Active Role</p>
                        <p className="text-sm font-semibold text-emerald-500">{role || 'ROLE_ADMIN'}</p>
                    </div>
                    <button
                        onClick={logout}
                        className="w-full flex items-center gap-3 px-4 py-2 text-slate-400 hover:text-rose-400 transition-colors"
                    >
                        <LogOut size={18} />
                        <span className="text-sm font-medium">Clear Session</span>
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col overflow-hidden bg-slate-900">
                <header className="h-16 bg-slate-950/80 backdrop-blur-sm border-b border-slate-800/50 flex items-center px-8 shrink-0 z-10 sticky top-0 justify-between">
                    <h2 className="text-lg font-semibold text-slate-100">System Administration & Compliance</h2>
                    <div className="flex items-center gap-2 text-sm text-emerald-400 bg-emerald-400/10 px-3 py-1 rounded-full border border-emerald-400/20">
                        <Activity size={14} /> All Systems Operational
                    </div>
                </header>
                <div className="flex-1 overflow-auto p-8 relative">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default AdminLayout;
