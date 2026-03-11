import React from 'react';

const VocabularyActivity = ({ onAnswer }) => {
    // Mock Data for Phase 5.1
    const targetWord = "Apple";
    const imageUrl = "🍎"; // Placeholder for an actual image asset
    
    const options = ["Banana", "Apple", "Orange"];

    return (
        <div className="flex flex-col items-center justify-center w-full max-w-4xl animate-fade-in">
            
            {/* Visual Subject */}
            <div className="text-9xl mb-4 drop-shadow-md">
                {imageUrl}
            </div>
            
            <div className="text-4xl font-bold text-slate-700 tracking-tight mb-16">
                {targetWord}
            </div>

            {/* Answer Buttons (Large, Touch-Friendly) */}
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full px-8">
                {options.map((opt, idx) => (
                    <button 
                        key={idx}
                        onClick={() => onAnswer(opt)}
                        className="py-6 px-4 bg-white border-4 border-slate-200 rounded-3xl text-3xl font-medium text-slate-700 hover:bg-blue-50 hover:border-blue-400 hover:text-blue-700 hover:scale-105 active:scale-95 transition-all shadow-sm"
                        style={{ minHeight: '100px' }} // "min height 70px" spec exceeded for easier touch
                    >
                        {opt}
                    </button>
                ))}
            </div>

        </div>
    );
};

export default VocabularyActivity;
