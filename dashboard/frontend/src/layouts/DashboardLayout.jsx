import React from 'react';
import { Outlet, Navigate, NavLink } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { LayoutDashboard, Brain, Activity, Target, Network, LogOut } from 'lucide-react';

const DashboardLayout = () => {
    const { isAuthenticated, role, logout } = useAuthStore();

    // Bypassing for dev scaffold.
    if (!isAuthenticated && process.env.NODE_ENV === 'production') {
        return <Navigate to="/login" replace />;
    }

    const navItems = [
        { path: '/', label: 'Overview & ZPD', icon: <Target size={20} /> },
        { path: '/emotions', label: 'Emotional Stability', icon: <Activity size={20} /> },
        { path: '/xai', label: 'Explainable AI', icon: <Brain size={20} /> },
        { path: '/interventions', label: 'Tool Intelligence', icon: <LayoutDashboard size={20} /> },
        { path: '/graph', label: 'Knowledge Graph', icon: <Network size={20} /> },
    ];

    return (
        <div className="flex h-screen bg-gray-900 text-slate-200">
            {/* Sidebar */}
            <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
                <div className="p-6 border-b border-gray-700 mb-4 flex items-center gap-3">
                    <Brain className="text-primary-400" size={28} />
                    <h1 className="text-xl font-bold tracking-tight text-white">LaRa Intel</h1>
                </div>

                <nav className="flex-1 px-4 space-y-2">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${isActive
                                    ? 'bg-primary-500/10 text-primary-400 border border-primary-500/20'
                                    : 'text-slate-400 hover:text-white hover:bg-gray-700/50'
                                }`
                            }
                        >
                            {item.icon}
                            <span className="font-medium text-sm">{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="p-4 border-t border-gray-700">
                    <div className="px-4 py-3 bg-gray-900/50 rounded-lg mb-3 border border-gray-700">
                        <p className="text-xs text-slate-400 uppercase tracking-wider mb-1">Active Role</p>
                        <p className="text-sm font-semibold text-primary-400">{role || 'ROLE_CLINICIAN'}</p>
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
            <main className="flex-1 flex flex-col overflow-hidden">
                <header className="h-16 bg-gray-900/80 backdrop-blur-sm border-b border-gray-700/50 flex items-center px-8 shrink-0 z-10 sticky top-0">
                    <h2 className="text-lg font-semibold text-slate-100">Clinical Dashboard</h2>
                </header>
                <div className="flex-1 overflow-auto p-8 relative">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default DashboardLayout;
