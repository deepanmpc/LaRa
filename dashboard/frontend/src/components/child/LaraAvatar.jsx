import React from 'react';

const LaraAvatar = ({ state, isDistracted }) => {
    // Required Spec States: idle, speaking, waiting, celebrating

    // Tailwind animation classes mapped to state
    let animationClass = "";
    let expression = "😊";
    
    switch (state) {
        case 'idle':
            animationClass = "animate-pulse-slow"; // Gentle breathing
            expression = "😊";
            break;
        case 'speaking':
            animationClass = "animate-custom-bounce"; // Mouth movement abstraction
            expression = "💬";
            break;
        case 'waiting':
            animationClass = "animate-pulse drop-shadow-[0_0_15px_rgba(59,130,246,0.6)]"; // Soft glowing pulse
            expression = "🤔";
            break;
        case 'celebrating':
            animationClass = "animate-custom-bounce-wide scale-110 drop-shadow-[0_0_20px_rgba(250,204,21,0.8)]"; // Bounce + sparkle ring
            expression = "🎉";
            break;
        default:
            animationClass = "";
            expression = "😊";
    }

    if (isDistracted) {
        // Overlay a wave animation (Phase 8) if distracted
        animationClass += " animate-[wiggle_1s_ease-in-out_infinite]"; 
        expression = "👋";
    }

    return (
        <div className={`relative flex items-center justify-center w-[120px] h-[120px] rounded-full bg-blue-100 border-4 border-blue-500 shadow-xl transition-all duration-300 ${animationClass}`}>
            
            {/* Minimal Avatar Face Abstraction */}
            <div className="text-6xl flex items-center justify-center w-full h-full pb-2">
                {expression}
            </div>

            {/* Sparkles for Celeb */}
            {state === 'celebrating' && (
                <>
                <div className="absolute -top-4 -right-2 text-2xl animate-spin">✨</div>
                <div className="absolute bottom-0 -left-4 text-2xl animate-spin delay-75">✨</div>
                </>
            )}

        </div>
    );
};

export default LaraAvatar;
