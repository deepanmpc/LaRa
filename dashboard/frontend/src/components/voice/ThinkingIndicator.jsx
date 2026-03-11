import React from 'react';

const ThinkingIndicator = ({ isVisible }) => {
    return (
        <div className={`flex items-center justify-center transition-opacity duration-500 h-24 ${isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
            <div className="flex gap-3">
                <div className="w-4 h-4 rounded-full bg-slate-300 animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-4 h-4 rounded-full bg-slate-400 animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-4 h-4 rounded-full bg-slate-500 animate-bounce" style={{ animationDelay: '300ms' }}></div>
            </div>
        </div>
    );
};

export default ThinkingIndicator;
