import React from 'react';
import { Outlet, Navigate, NavLink } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { LayoutDashboard, Brain, LogOut, HeartPulse } from 'lucide-react';

const ClinicianLayout = () => {
    const { isAuthenticated, role, logout } = useAuthStore();

    // Bypassing for dev scaffold.
    if (!isAuthenticated && process.env.NODE_ENV === 'production') {
        return <Navigate to="/login" replace />;
    }

    const navItems = [
        { path: '/dashboard/clinical', label: 'Clinical Dashboard', icon: <HeartPulse size={20} /> },
        { path: '/session', label: 'Session Controls', icon: <LayoutDashboard size={20} /> }
    ];

    return (
        <div className="flex h-screen bg-slate-50 text-slate-800 font-sans">
            {/* Sidebar (Cleaned up from deep black to light medical mode) */}
            <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shadow-sm z-20">
                <div className="p-6 border-b border-slate-100 mb-4 flex items-center gap-3">
                    <Brain className="text-blue-600" size={28} />
                    <h1 className="text-xl font-bold tracking-tight text-slate-800">LaRa <span className="text-blue-600 font-light">Medical</span></h1>
                </div>

                <nav className="flex-1 px-4 space-y-2">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center gap-3 px-4 py-3 rounded-lg transition-colors font-medium ${isActive
                                    ? 'bg-blue-50 text-blue-700 border border-blue-100'
                                    : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'
                                }`
                            }
                        >
                            {item.icon}
                            <span className="text-sm">{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="p-6 border-t border-slate-100">
                    <div className="px-4 py-3 bg-slate-50 rounded-lg mb-4 border border-slate-200">
                        <p className="text-[10px] text-slate-400 uppercase tracking-widest mb-1 font-semibold">Active Role</p>
                        <p className="text-sm font-bold text-slate-700">{role || 'ROLE_CLINICIAN'}</p>
                    </div>
                    <button
                        onClick={logout}
                        className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-white border border-slate-200 rounded-lg text-slate-500 hover:text-rose-600 hover:border-rose-200 hover:bg-rose-50 transition-colors shadow-sm"
                    >
                        <LogOut size={16} />
                        <span className="text-sm font-semibold">Log Out</span>
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col overflow-hidden bg-slate-50 relative">
                <div className="flex-1 overflow-auto">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default ClinicianLayout;
