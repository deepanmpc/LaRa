import React from 'react';
import { Fingerprint, Calendar, Activity } from 'lucide-react';

const PatientSnapshotBar = ({ studentId, lastSessionDate, status }) => {

    // Status visual mapping (mimicking hospital triage logic)
    const statusConfig = {
        'Stable': { bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200', dot: 'bg-emerald-500' },
        'Improving': { bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200', dot: 'bg-blue-500' },
        'Watch': { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', dot: 'bg-amber-500' },
        'Critical': { bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200', dot: 'bg-rose-500' }
    };

    const config = statusConfig[status] || statusConfig['Stable'];

    return (
        <div className="bg-white border border-slate-200 rounded-xl p-5 shadow-sm flex flex-col md:flex-row md:items-center justify-between gap-4">

            {/* Identify Patient */}
            <div className="flex items-center gap-4">
                <div className="h-12 w-12 bg-slate-100 rounded-full flex items-center justify-center text-slate-400 border border-slate-200">
                    <Fingerprint size={24} />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-slate-800 tracking-tight">{studentId}</h2>
                    <div className="flex justify-between items-center text-sm text-slate-500 gap-3 mt-0.5">
                        <span className="flex items-center gap-1"><Calendar size={14} /> Age: 8</span>
                        <span className="flex items-center gap-1"><Activity size={14} /> ID: {Math.random().toString(36).substr(2, 6).toUpperCase()}</span>
                    </div>
                </div>
            </div>

            {/* Core Snapshot Info */}
            <div className="flex flex-col md:flex-row md:items-center gap-4 md:gap-8">
                <div className="flex flex-col text-sm border-l-2 border-slate-100 pl-4">
                    <span className="text-slate-400 font-medium uppercase tracking-wider text-[10px]">Last Session</span>
                    <span className="text-slate-700 font-semibold">{lastSessionDate}</span>
                </div>

                <div className="flex items-center gap-3 border-l-2 border-slate-100 pl-4 py-1">
                    <div className="flex flex-col">
                        <span className="text-slate-400 font-medium uppercase tracking-wider text-[10px]">Overall Status</span>
                        {/* Overall Status Badge */}
                        <div className={`mt-0.5 flex items-center gap-2 px-3 py-1 rounded-full border text-xs font-bold tracking-wide ${config.bg} ${config.text} ${config.border}`}>
                            <span className={`h-2 w-2 rounded-full ${config.dot}`}></span>
                            {status.toUpperCase()}
                        </div>
                    </div>
                </div>

                <div className="flex flex-col text-sm border-l-2 border-slate-100 pl-4">
                    <span className="text-slate-400 font-medium uppercase tracking-wider text-[10px]">Confidence</span>
                    <span className="text-slate-700 font-semibold flex items-center gap-1">
                        High <span className="text-slate-300 text-xs">(89%)</span>
                    </span>
                </div>
            </div>

        </div>
    );
};

export default PatientSnapshotBar;
