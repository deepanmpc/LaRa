import React from 'react';

const SocialScenariosActivity = ({ onAnswer }) => {
    // Mock Data for Phase 5.3
    const scenePrompt = "How is the boy feeling?";
    const sceneImage = "👦🎈💥"; // Abstract representation of losing a balloon
    
    const emotions = [
        { emoji: "😊", label: "Happy" },
        { emoji: "😢", label: "Sad" },
        { emoji: "😠", label: "Angry" },
        { emoji: "😮", label: "Surprised" }
    ];

    return (
        <div className="flex flex-col items-center justify-center w-full max-w-5xl animate-fade-in text-center px-4">
            
            {/* Context / Scene */}
            <div className="text-3xl font-medium text-slate-600 mb-8">
                {scenePrompt}
            </div>

            <div className="text-9xl mb-16 drop-shadow-sm bg-white p-12 rounded-[3rem] border-4 border-slate-100">
                {sceneImage}
            </div>

            {/* Emotion Choices (Large Emoji Buttons) */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-6 w-full">
                {emotions.map((emotion, idx) => (
                    <button 
                        key={idx}
                        onClick={() => onAnswer(emotion.label)}
                        className="flex flex-col items-center justify-center py-8 bg-white border-4 border-slate-200 rounded-[30px] hover:border-emerald-400 hover:bg-emerald-50 hover:scale-105 active:scale-95 transition-all shadow-sm group cursor-pointer"
                        style={{ minHeight: '160px' }}
                    >
                        <span className="text-6xl mb-4 group-hover:scale-110 transition-transform">
                            {emotion.emoji}
                        </span>
                        <span className="text-2xl font-bold text-slate-700">
                            {emotion.label}
                        </span>
                    </button>
                ))}
            </div>

        </div>
    );
};

export default SocialScenariosActivity;
