import React from 'react';

const LaraAvatar = ({ state }) => {
    // Abstract representation mapping
    let animationClass = "";
    
    switch (state) {
        case 'idle':
            animationClass = "animate-pulse-slow opacity-80 scale-100";
            break;
        case 'listening':
            animationClass = "animate-pulse opacity-100 scale-110 drop-shadow-[0_0_20px_rgba(59,130,246,0.6)]";
            break;
        case 'thinking':
            animationClass = "animate-custom-bounce opacity-90 scale-100";
            break;
        case 'speaking':
            animationClass = "animate-custom-bounce-wide opacity-100 scale-110 drop-shadow-[0_0_25px_rgba(37,99,235,0.8)]";
            break;
        default:
            animationClass = "opacity-80";
    }

    return (
        <div className="flex flex-col items-center justify-center transition-all duration-700 ease-in-out">
            <div className={`w-36 h-36 rounded-full bg-gradient-to-tr from-blue-600 to-blue-400 flex items-center justify-center text-6xl shadow-xl transition-all duration-500 ${animationClass}`}>
                <span className="drop-shadow-sm transition-transform duration-300">
                    {state === 'listening' ? '🎧' : '🤖'}
                </span>
            </div>
            
            {/* Status Text (Subtle) */}
            <div className="mt-6 text-sm font-medium text-slate-400 tracking-widest uppercase transition-opacity duration-500">
                {state === 'idle' && 'Ready'}
                {state === 'listening' && 'Listening...'}
                {state === 'thinking' && 'Thinking...'}
                {state === 'speaking' && 'Speaking'}
            </div>
        </div>
    );
};

export default LaraAvatar;
