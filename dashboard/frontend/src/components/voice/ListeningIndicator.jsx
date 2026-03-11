import React from 'react';

const ListeningIndicator = ({ isVisible }) => {
    return (
        <div className={`flex items-center justify-center transition-opacity duration-700 h-24 ${isVisible ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
            <div className="relative flex items-center justify-center">
                {/* Sonar Rings */}
                <div className="absolute w-32 h-32 bg-blue-100 rounded-full animate-ping-slow opacity-60"></div>
                <div className="absolute w-24 h-24 bg-blue-200 rounded-full animate-ping-slower opacity-80"></div>
                
                {/* Core Mic Visual */}
                <div className="relative z-10 w-16 h-16 bg-blue-500 rounded-full flex items-center justify-center shadow-lg text-white">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        <line x1="12" x2="12" y1="19" y2="22" />
                    </svg>
                </div>
            </div>
        </div>
    );
};

export default ListeningIndicator;
