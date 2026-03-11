import React, { useState } from 'react';

const StorySequencingActivity = ({ onAnswer }) => {
    // Mock Data for Phase 5.2 (Multiple scene cards)
    const [scenes, setScenes] = useState([
        { id: 1, image: "🌱", label: "Plant Seed", order: null },
        { id: 2, image: "🌻", label: "Flower Grows", order: null },
        { id: 3, image: "💧", label: "Water Seed", order: null }
    ]);

    const [currentStep, setCurrentStep] = useState(1);

    const handleSelect = (id) => {
        // Prevent re-clicking an already ordered item
        if (scenes.find(s => s.id === id).order !== null) return;

        const updatedScenes = scenes.map(scene => 
            scene.id === id ? { ...scene, order: currentStep } : scene
        );
        
        setScenes(updatedScenes);
        setCurrentStep(prev => prev + 1);
    };

    const handleReset = () => {
        setScenes(scenes.map(s => ({ ...s, order: null })));
        setCurrentStep(1);
    };

    const handleSubmit = () => {
        // Create ordered answer array based on child's selection sequence
        const answerSequence = scenes.filter(s => s.order !== null).sort((a,b) => a.order - b.order).map(s => s.label);
        onAnswer(answerSequence);
    };

    const isComplete = currentStep > scenes.length;

    return (
        <div className="flex flex-col items-center justify-center w-full max-w-5xl animate-fade-in px-4">
            
            <div className="text-2xl font-medium text-slate-500 mb-12 uppercase tracking-widest">
                What happens next?
            </div>

            {/* Scene Cards (Large, Touch-Friendly) */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full mb-16">
                {scenes.map((scene) => (
                    <button 
                        key={scene.id}
                        onClick={() => handleSelect(scene.id)}
                        disabled={scene.order !== null}
                        className={`relative flex flex-col items-center justify-center py-12 px-6 bg-white border-4 rounded-[40px] shadow-sm transition-all duration-300 ${
                            scene.order !== null 
                                ? 'border-emerald-400 scale-95 opacity-80 cursor-default' 
                                : 'border-slate-200 hover:border-blue-400 hover:scale-105 active:scale-95 cursor-pointer'
                        }`}
                        style={{ minHeight: '220px' }}
                    >
                        {/* Selected Sequence Number Indicator */}
                        {scene.order !== null && (
                            <div className="absolute -top-6 -right-6 w-14 h-14 bg-emerald-500 text-white rounded-full flex items-center justify-center text-3xl font-bold shadow-lg border-4 border-white z-10 animate-bounce-in">
                                {scene.order}
                            </div>
                        )}

                        <div className="text-8xl drop-shadow-sm mb-4">
                            {scene.image}
                        </div>
                    </button>
                ))}
            </div>

            {/* Submit / Reset Actions */}
            <div className="flex gap-6 h-24">
                {isComplete && (
                    <button 
                        onClick={handleSubmit}
                        className="px-16 py-6 bg-emerald-500 border-4 border-emerald-600 rounded-full text-4xl font-bold text-white shadow-xl hover:bg-emerald-400 hover:scale-105 active:scale-95 transition-all tracking-wide animate-fade-in"
                    >
                        Done!
                    </button>
                )}
                {currentStep > 1 && !isComplete && (
                    <button 
                        onClick={handleReset}
                        className="px-8 py-4 bg-slate-100 border-4 border-slate-300 rounded-full text-xl font-bold text-slate-500 hover:bg-slate-200 hover:scale-105 active:scale-95 transition-all"
                    >
                        Start Over
                    </button>
                )}
            </div>

        </div>
    );
};

export default StorySequencingActivity;
