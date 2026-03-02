import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';
import Webcam from 'react-webcam';
import { Camera, Plus, UserCircle, CheckCircle2, AlertCircle, ArrowRight, Play } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_BASE = 'http://localhost:8080/api/students';

const SessionLauncher = () => {
    const navigate = useNavigate();
    const [view, setView] = useState('LIST'); // LIST, ADD, CONFIRM_IDENTITY, SESSION_ACTIVE
    const [students, setStudents] = useState([]);
    const [selectedStudent, setSelectedStudent] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    // Form State
    const [formData, setFormData] = useState({ name: '', age: '', preferredName: '', notes: '' });

    // Webcam State
    const webcamRef = useRef(null);
    const [isScanning, setIsScanning] = useState(false);
    const [scanResult, setScanResult] = useState(null);

    useEffect(() => {
        fetchStudents();
    }, []);

    const fetchStudents = async () => {
        try {
            const res = await axios.get(API_BASE);
            setStudents(res.data);
            setIsLoading(false);
        } catch (error) {
            console.error("Failed to load children", error);
            setIsLoading(false);
        }
    };

    const handleAddSubmit = async (e) => {
        e.preventDefault();
        try {
            const res = await axios.post(`${API_BASE}/add`, formData);
            setStudents([...students, res.data]);
            setView('LIST');
            setFormData({ name: '', age: '', preferredName: '', notes: '' });
        } catch (error) {
            console.error("Failed to add child", error);
        }
    };

    const handleSelectChild = (student) => {
        setSelectedStudent(student);
        setView('CONFIRM_IDENTITY');
    };

    const triggerScan = () => {
        setIsScanning(true);
        // Mock identity validation latency
        setTimeout(() => {
            setIsScanning(false);
            setScanResult('MATCH'); // Always mock match for now
        }, 1500);
    };

    const renderList = () => (
        <div className="max-w-4xl mx-auto py-12 px-6">
            <div className="text-center mb-12">
                <h1 className="text-4xl font-extrabold text-blue-900 tracking-tight">Welcome to LaRa!</h1>
                <p className="text-lg text-blue-600 mt-2">Who is ready to learn today?</p>
            </div>

            {isLoading ? (
                <div className="flex justify-center"><div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div></div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {students.map((child) => (
                        <div 
                            key={child.studentIdHashed}
                            onClick={() => handleSelectChild(child)}
                            className="bg-white rounded-3xl p-6 shadow-sm border border-blue-100 hover:shadow-md hover:border-blue-300 transition-all cursor-pointer group text-center flex flex-col items-center"
                        >
                            <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-4 group-hover:bg-blue-500 transition-colors">
                                <UserCircle size={40} className="text-blue-500 group-hover:text-white" />
                            </div>
                            <h3 className="text-xl font-bold text-slate-800">{child.preferredName || child.name}</h3>
                            <p className="text-sm text-slate-400 mt-1">Age {child.age}</p>
                            <button className="mt-6 px-6 py-2 bg-blue-50 text-blue-600 rounded-full text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                                Start Session
                            </button>
                        </div>
                    ))}

                    <div 
                        onClick={() => setView('ADD')}
                        className="bg-blue-50/50 rounded-3xl p-6 border-2 border-dashed border-blue-200 hover:bg-blue-50 hover:border-blue-300 transition-all cursor-pointer text-center flex flex-col items-center justify-center min-h-[250px]"
                    >
                        <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mb-4 shadow-sm text-blue-400">
                            <Plus size={32} />
                        </div>
                        <h3 className="text-lg font-bold text-slate-700">Add New Child</h3>
                    </div>
                </div>
            )}
        </div>
    );

    const renderAddForm = () => (
        <div className="max-w-lg mx-auto py-12 px-6">
            <button onClick={() => setView('LIST')} className="text-blue-500 hover:text-blue-700 mb-6 font-medium text-sm">
                &larr; Back to selection
            </button>
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100">
                <h2 className="text-2xl font-bold text-slate-800 mb-6">Let's meet someone new!</h2>
                <form onSubmit={handleAddSubmit} className="space-y-5">
                    <div>
                        <label className="block text-sm font-semibold text-slate-600 mb-1">Full Name</label>
                        <input required type="text" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all" placeholder="E.g., Leo Smith" />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-slate-600 mb-1">Preferred Name / Nickname</label>
                        <input type="text" value={formData.preferredName} onChange={e => setFormData({...formData, preferredName: e.target.value})} className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all" placeholder="What should LaRa call them?" />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-slate-600 mb-1">Age</label>
                        <input required type="number" min="3" max="18" value={formData.age} onChange={e => setFormData({...formData, age: e.target.value})} className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all" />
                    </div>
                    <div>
                        <label className="block text-sm font-semibold text-slate-600 mb-1">Caregiver Notes (Optional)</label>
                        <textarea value={formData.notes} onChange={e => setFormData({...formData, notes: e.target.value})} className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all h-24" placeholder="Any special instructions for today? (Kept hidden from the child)" />
                    </div>
                    <button type="submit" className="w-full py-4 bg-blue-500 hover:bg-blue-600 text-white rounded-xl font-bold tracking-wide transition-colors mt-4">
                        Save & Add Child
                    </button>
                </form>
            </div>
        </div>
    );

    const renderConfirmIdentity = () => (
        <div className="max-w-2xl mx-auto py-12 px-6 flex flex-col items-center">
            <button onClick={() => {setView('LIST'); setScanResult(null);}} className="self-start text-blue-500 hover:text-blue-700 mb-6 font-medium text-sm">
                &larr; Not {selectedStudent?.preferredName || selectedStudent?.name}?
            </button>
            
            <div className="bg-white rounded-3xl p-8 shadow-sm border border-blue-100 w-full text-center overflow-hidden">
                <h2 className="text-2xl font-bold text-slate-800 mb-2">Hello, friend!</h2>
                <p className="text-slate-500 mb-8">LaRa is getting ready. Let's make sure it's really you.</p>

                <div className="relative w-64 h-64 mx-auto rounded-full overflow-hidden border-4 border-slate-100 shadow-inner bg-slate-50 mb-8">
                    <Webcam
                        audio={false}
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        className="object-cover w-full h-full"
                        mirrored={true}
                    />
                    
                    {/* Scanning Overlay */}
                    {isScanning && (
                        <div className="absolute inset-0 bg-blue-500/20 flex items-center justify-center">
                            <div className="w-full h-1 bg-blue-400 animate-pulse absolute top-1/2 shadow-[0_0_15px_rgba(59,130,246,0.8)]"></div>
                        </div>
                    )}
                </div>

                {!scanResult ? (
                    <button 
                        onClick={triggerScan}
                        disabled={isScanning}
                        className={`px-8 py-4 rounded-full font-bold inline-flex items-center gap-2 transition-all ${isScanning ? 'bg-slate-100 text-slate-400' : 'bg-blue-500 hover:bg-blue-600 text-white'}`}
                    >
                        {isScanning ? (
                            <>Looking...</>
                        ) : (
                            <><Camera size={20} /> I'm ready!</>
                        )}
                    </button>
                ) : (
                    <div className="animate-fade-in-up">
                        <div className="inline-flex items-center justify-center w-12 h-12 bg-emerald-100 text-emerald-500 rounded-full mb-4">
                            <CheckCircle2 size={24} />
                        </div>
                        <h3 className="text-xl font-bold text-slate-800 mb-1">
                            This looks like {selectedStudent?.preferredName || selectedStudent?.name}!
                        </h3>
                        <p className="text-slate-500 mb-8 text-sm">Identity confirmed. The curriculum is ready.</p>
                        
                        <div className="flex justify-center gap-4">
                            <button 
                                onClick={() => setView('SESSION_ACTIVE')}
                                className="px-8 py-4 bg-emerald-500 hover:bg-emerald-600 text-white rounded-full font-bold inline-flex items-center gap-2 transition-all shadow-lg hover:-translate-y-1"
                            >
                                <Play size={20} /> Continue Learning
                            </button>
                            <button className="px-6 py-4 bg-slate-100 text-slate-600 hover:bg-slate-200 rounded-full font-semibold transition-all">
                                Switch Path
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );

    const renderSessionActive = () => (
        <div className="h-screen w-full bg-blue-50 flex items-center justify-center relative overflow-hidden">
            {/* Soft background decor */}
            <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-cyan-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob"></div>
            <div className="absolute top-[20%] right-[-10%] w-96 h-96 bg-purple-200 rounded-full mix-blend-multiply filter blur-3xl opacity-30 animate-blob animation-delay-2000"></div>
            
            <div className="text-center z-10 max-w-lg">
                <div className="w-24 h-24 bg-white rounded-3xl shadow-lg flex items-center justify-center mx-auto mb-8 animate-bounce">
                    <UserCircle size={48} className="text-blue-400" />
                </div>
                <h1 className="text-4xl font-extrabold text-slate-800 mb-4 tracking-tight">
                    Let's play and learn, {selectedStudent?.preferredName || selectedStudent?.name}!
                </h1>
                <p className="text-slate-500 text-lg mb-12">
                    LaRa is listening. The AI curriculum is running silently in the background.
                </p>
                
                <button 
                    onClick={() => navigate('/dashboard')}
                    className="px-6 py-2 bg-white text-slate-500 hover:text-blue-500 rounded-full text-sm font-semibold shadow-sm transition-all"
                >
                    Return to Clinical Admin Dashboard
                </button>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-50 text-slate-800 font-sans selection:bg-blue-200">
            {view === 'LIST' && renderList()}
            {view === 'ADD' && renderAddForm()}
            {view === 'CONFIRM_IDENTITY' && renderConfirmIdentity()}
            {view === 'SESSION_ACTIVE' && renderSessionActive()}
        </div>
    );
};

export default SessionLauncher;
