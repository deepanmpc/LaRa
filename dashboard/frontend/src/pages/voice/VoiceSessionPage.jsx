import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import LaraAvatar from '../../components/voice/LaraAvatar';
import SpeechBubble from '../../components/voice/SpeechBubble';
import ListeningIndicator from '../../components/voice/ListeningIndicator';
import ThinkingIndicator from '../../components/voice/ThinkingIndicator';

const VoiceSessionPage = () => {
    const { childId, sessionUuid } = useParams();

    // Voice State Machine: idle -> listening -> thinking -> speaking -> ...
    const [voiceState, setVoiceState] = useState('idle');
    const [speechText, setSpeechText] = useState("Hi there! I'm LaRa.");

    // Mock State Machine Execution (For demonstration purposes)
    useEffect(() => {
        let timer;
        const runCycle = () => {
            if (voiceState === 'idle') {
                // Initial load: stay idle for 2s, then start conversation
                timer = setTimeout(() => {
                    setVoiceState('speaking');
                    setSpeechText("Hello! What would you like to talk about today?");
                }, 2000);
            } else if (voiceState === 'speaking') {
                // Speak for 3 seconds, then listen
                timer = setTimeout(() => {
                    setVoiceState('listening');
                    setSpeechText("");
                }, 3000);
            } else if (voiceState === 'listening') {
                // Listen for 4 seconds, then think
                timer = setTimeout(() => {
                    setVoiceState('thinking');
                }, 4000);
            } else if (voiceState === 'thinking') {
                // Think for 2 seconds, then speak
                timer = setTimeout(() => {
                    setVoiceState('speaking');
                    setSpeechText("That sounds really fun!");
                }, 2000);
            }
        };

        runCycle();

        return () => clearTimeout(timer);
    }, [voiceState]);

    return (
        <div className="fixed inset-0 min-h-screen w-full bg-slate-50 flex flex-col items-center justify-center font-sans overflow-hidden">
            
            {/* Top Zone: Speech Text */}
            <div className="flex-1 w-full flex items-end justify-center pb-12">
                <SpeechBubble 
                    text={speechText} 
                    isVisible={voiceState === 'speaking' || voiceState === 'idle'} 
                />
            </div>

            {/* Middle Zone: Avatar */}
            <div className="flex-none flex items-center justify-center py-8">
                <LaraAvatar state={voiceState} />
            </div>

            {/* Bottom Zone: Indicators */}
            <div className="flex-1 w-full flex items-start justify-center pt-12">
                {/* We render both but control visibility via CSS opacity to prevent layout shifts */}
                <div className="relative flex items-center justify-center">
                    <div className={`absolute transition-opacity duration-500 delay-100 ${voiceState === 'listening' ? 'opacity-100' : 'opacity-0'}`}>
                        <ListeningIndicator isVisible={voiceState === 'listening'} />
                    </div>
                    
                    <div className={`absolute transition-opacity duration-500 delay-100 ${voiceState === 'thinking' ? 'opacity-100' : 'opacity-0'}`}>
                        <ThinkingIndicator isVisible={voiceState === 'thinking'} />
                    </div>
                </div>
            </div>

        </div>
    );
};

export default VoiceSessionPage;
