import React from 'react';
import { Outlet, Navigate, NavLink, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { LogOut, Heart, BookOpen, UserCircle, Star } from 'lucide-react';

const CaregiverLayout = () => {
    const { isAuthenticated, role, logout } = useAuthStore();
    const navigate = useNavigate();

    // Guard placeholder, bypassing for dev
    if (!isAuthenticated && process.env.NODE_ENV === 'production') {
        return <Navigate to="/login" replace />;
    }

    const navItems = [
        { path: '/caregiver/simple', label: 'Today\'s Summary', icon: <Star size={24} /> },
        { path: '/session', label: 'Start Session', icon: <Heart size={24} /> }
    ];

    return (
        <div className="flex h-screen bg-slate-50 text-slate-800 font-sans">
            {/* Sidebar */}
            <aside className="w-64 bg-white border-r border-blue-100 flex flex-col shadow-sm z-20">
                <div className="p-6 border-b border-blue-50 mb-4 flex flex-col items-center gap-2">
                    <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center text-blue-500 mb-2">
                        <UserCircle size={40} />
                    </div>
                    <h1 className="text-xl font-extrabold tracking-tight text-blue-900">LaRa Care</h1>
                    <span className="text-xs font-semibold text-blue-400 uppercase tracking-widest bg-blue-50 px-3 py-1 rounded-full">Family View</span>
                </div>

                <nav className="flex-1 px-4 space-y-3 mt-4">
                    {navItems.map((item) => (
                        <NavLink
                            key={item.path}
                            to={item.path}
                            className={({ isActive }) =>
                                `flex items-center gap-4 px-5 py-4 rounded-2xl transition-all font-bold ${isActive
                                    ? 'bg-blue-500 text-white shadow-md'
                                    : 'text-slate-500 hover:text-blue-600 hover:bg-blue-50'
                                }`
                            }
                        >
                            {item.icon}
                            <span className="text-base">{item.label}</span>
                        </NavLink>
                    ))}
                </nav>

                <div className="p-6">
                    <button
                        onClick={logout}
                        className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-rose-50 text-rose-500 hover:bg-rose-500 hover:text-white rounded-xl font-bold transition-colors"
                    >
                        <LogOut size={18} />
                        <span>Sign Out</span>
                    </button>

                    {/* Dev Only Button to traverse to Tier 2 Clinician View */}
                    <button
                        onClick={() => navigate('/')}
                        className="w-full mt-4 flex items-center justify-center gap-2 px-4 py-3 bg-slate-100 text-slate-400 hover:bg-slate-200 hover:text-slate-600 rounded-xl font-semibold transition-colors text-xs"
                    >
                        [Dev] Go to Admin/Clinician
                    </button>
                </div>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 flex flex-col overflow-hidden relative">
                {/* Soft background decor */}
                <div className="absolute top-[-5%] right-[-5%] w-[500px] h-[500px] bg-blue-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 pointer-events-none"></div>
                <div className="absolute bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-emerald-200 rounded-full mix-blend-multiply filter blur-3xl opacity-20 pointer-events-none"></div>

                <header className="h-20 bg-white/60 backdrop-blur-md border-b border-blue-50/50 flex items-center px-10 shrink-0 z-10 sticky top-0 shadow-sm">
                    <h2 className="text-2xl font-bold text-slate-800 flex items-center gap-3">
                        <BookOpen className="text-blue-400" size={28} /> Learning & Wellbeing
                    </h2>
                </header>
                <div className="flex-1 overflow-auto p-10 z-10">
                    <Outlet />
                </div>
            </main>
        </div>
    );
};

export default CaregiverLayout;
