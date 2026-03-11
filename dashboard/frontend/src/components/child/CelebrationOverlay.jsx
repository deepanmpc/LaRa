import React from 'react';

const CelebrationOverlay = ({ isVisible }) => {
    if (!isVisible) return null;

    // Spec Phase 7: Appears for 2 seconds (Timing controlled by parent), Shows stars/confetti, Praise message.

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center pointer-events-none w-full h-full">
            
            {/* Background Dimmer */}
            <div className="absolute inset-0 bg-black/20 animate-fade-in"></div>

            {/* Exploding Stars / Confetti Abstraction */}
            <div className="absolute inset-0 overflow-hidden">
                <div className="absolute top-1/4 left-1/4 text-6xl animate-bounce-in drop-shadow-lg delay-75">⭐</div>
                <div className="absolute top-1/3 right-1/4 text-8xl animate-bounce-in drop-shadow-lg scale-125 delay-100">🌟</div>
                <div className="absolute bottom-1/3 left-1/3 text-6xl animate-bounce-in drop-shadow-lg delay-150">✨</div>
                <div className="absolute bottom-1/4 right-1/3 text-7xl animate-bounce-in drop-shadow-lg delay-75">⭐</div>
            </div>

            {/* Praise Message Container */}
            <div className="relative z-10 bg-white border-8 border-emerald-400 px-16 py-10 rounded-[50px] shadow-2xl animate-bounce-in flex flex-col items-center transform scale-125">
                <div className="text-8xl mb-4">🎉</div>
                <h1 className="text-6xl font-black text-emerald-500 tracking-tight uppercase">
                    Great Job!
                </h1>
            </div>

        </div>
    );
};

export default CelebrationOverlay;
