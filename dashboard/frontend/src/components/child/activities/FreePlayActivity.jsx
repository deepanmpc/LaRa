import React from 'react';
import { Mic } from 'lucide-react';

const FreePlayActivity = () => {
    // Phase 5.5 Spec: Mic button with pulse animation, but NO actual audio capture UI logic here.
    // Audio is handled silently by backend STT pipeline via a webcam/mic hardware feed.

    return (
        <div className="flex flex-col items-center justify-center w-full max-w-4xl animate-fade-in text-center px-4">
            
            <div className="text-3xl font-medium text-slate-500 mb-20 uppercase tracking-widest animate-pulse">
                Tell me a story!
            </div>

            {/* Mic Button: Large circle, pulse animation, no actual browser recording logic */}
            <div className="relative flex justify-center items-center">
                
                {/* Expanding sonar rings */}
                <div className="absolute w-64 h-64 bg-rose-200 rounded-full animate-ping-slow opacity-75"></div>
                <div className="absolute w-48 h-48 bg-rose-300 rounded-full animate-ping-slower opacity-75"></div>
                
                {/* Core Mic Button */}
                <button 
                    className="relative z-10 flex items-center justify-center w-40 h-40 bg-rose-500 border-8 border-rose-100 rounded-full text-white shadow-2xl hover:bg-rose-600 transition-colors"
                    aria-label="Microphone active indicator"
                >
                    <Mic size={64} strokeWidth={2.5} />
                </button>
            </div>

            <p className="mt-16 text-xl text-slate-400 font-medium">
                I'm listening...
            </p>

        </div>
    );
};

export default FreePlayActivity;
