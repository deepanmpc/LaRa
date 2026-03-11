import React from 'react';

const MathBasicsActivity = ({ onAnswer }) => {
    // Mock Data for Phase 5.4 (Visual Equation)
    const visualEquation = "🍎 🍎 🍎 + 🍎 🍎";
    const answerOptions = [3, 4, 5];

    return (
        <div className="flex flex-col items-center justify-center w-full max-w-4xl animate-fade-in text-center px-4">
            
            <div className="text-2xl font-medium text-slate-500 mb-8 uppercase tracking-widest">
                How many apples?
            </div>

            {/* Visual Equation */}
            <div className="text-7xl mb-16 p-12 bg-white border-4 border-slate-100 rounded-[40px] shadow-sm tracking-[0.5em]">
                {visualEquation}
            </div>

            {/* Number Square Buttons */}
            <div className="flex gap-8 justify-center">
                {answerOptions.map((num, idx) => (
                    <button 
                        key={idx}
                        onClick={() => onAnswer(num)}
                        className="flex items-center justify-center w-36 h-36 bg-blue-500 border-b-8 border-blue-600 rounded-[30px] text-6xl font-black text-white hover:bg-blue-400 hover:translate-y-1 hover:border-b-4 active:translate-y-2 active:border-b-0 transition-all shadow-lg"
                    >
                        {num}
                    </button>
                ))}
            </div>

        </div>
    );
};

export default MathBasicsActivity;
