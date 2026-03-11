import React from 'react';

const SpeechBubble = ({ text, isVisible }) => {
    return (
        <div 
            className={`transition-all duration-700 ease-in-out transform ${isVisible ? 'opacity-100 translate-y-0 scale-100' : 'opacity-0 translate-y-4 scale-95 pointer-events-none'}`}
            style={{ minHeight: '80px' }}
        >
            <p className="text-3xl md:text-4xl lg:text-5xl font-medium text-slate-700 text-center tracking-tight leading-snug px-8 max-w-4xl mx-auto">
                {text}
            </p>
        </div>
    );
};

export default SpeechBubble;
