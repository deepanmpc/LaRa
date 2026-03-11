import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import LaraAvatar from '../../components/child/LaraAvatar';
import ActivityArea from '../../components/child/ActivityArea';
import CelebrationOverlay from '../../components/child/CelebrationOverlay';

const ChildSessionPage = () => {
    const { childId, sessionUuid } = useParams();

    // Core State (as per spec)
    const [sessionType, setSessionType] = useState('VOCABULARY');
    const [activities, setActivities] = useState([]);
    const [currentActivityIndex, setCurrentActivityIndex] = useState(0);
    const [speechText, setSpeechText] = useState("Hi there! I'm LaRa. Let's play!");
    const [laraState, setLaraState] = useState('speaking'); // idle, speaking, waiting, celebrating
    const [celebration, setCelebration] = useState(false);
    
    // Distraction / Attention State
    const [isDistracted, setIsDistracted] = useState(false);
    const [isOffScreen, setIsOffScreen] = useState(false);

    // Mock initial load (Would normally fetch session data via sessionUuid)
    useEffect(() => {
        // Transition to idle after greeting
        const timer = setTimeout(() => {
            setLaraState('idle');
            setSpeechText("Can you find the apple?");
        }, 3000);
        return () => clearTimeout(timer);
    }, []);

    const handleAnswerSubmit = async (answer) => {
        // Mocking Phase 6: Response Handling
        console.log(`Submitting answer: ${answer} for session ${sessionUuid}`);
        
        // Mock network delay
        setLaraState('waiting');
        await new Promise(r => setTimeout(r, 800));

        // Mock Correct Answer Logic
        const isCorrect = true; // In reality, evaluate against backend
        
        if (isCorrect) {
            setLaraState('celebrating');
            setSpeechText("Great job!");
            setCelebration(true);
            
            // Hide celebration after 2 seconds
            setTimeout(() => {
                setCelebration(false);
                setLaraState('idle');
                setSpeechText("Let's try another one!");
                // Move to next activity...
            }, 2000);
        } else {
            setLaraState('speaking');
            setSpeechText("Not quite, let's try again!");
            setTimeout(() => setLaraState('idle'), 2000);
        }
    };

    return (
        <div className={`fixed inset-0 min-h-screen w-full bg-slate-50 flex flex-col font-sans transition-opacity duration-700 ${isOffScreen ? 'opacity-40' : 'opacity-100'}`}>
            
            {/* Phase 7: Overlay trigger */}
            <CelebrationOverlay isVisible={celebration} />

            {/* Top Zone: Avatar & Speech */}
            <div className="child-top-zone flex flex-col items-center justify-end h-1/3 pt-8 pb-4">
                
                <div className="relative mb-6">
                    {/* Speech Bubble */}
                    {speechText && (
                        <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-4 w-max max-w-md bg-white border-2 border-slate-100 shadow-xl rounded-3xl px-8 py-4 text-center z-10">
                            <p className="text-3xl font-medium text-slate-700 tracking-tight leading-snug">
                                {speechText}
                            </p>
                            {/* Triangle pointer */}
                            <div className="absolute top-full left-1/2 -translate-x-1/2 -mt-1 border-solid border-t-white border-t-8 border-x-transparent border-x-8 border-b-0 w-0 h-0"></div>
                        </div>
                    )}
                    
                    <LaraAvatar state={laraState} isDistracted={isDistracted} />
                </div>
            </div>

            {/* Mid Zone: Activity Router */}
            <div className="child-mid-zone flex-[2] flex items-center justify-center p-8">
                {isOffScreen ? (
                    <div className="text-4xl font-light text-slate-400 text-center">
                        I'll wait for you.
                    </div>
                ) : (
                    <ActivityArea 
                        sessionType={sessionType} 
                        onAnswer={handleAnswerSubmit} 
                    />
                )}
            </div>

            {/* Bottom Zone: Empty buffer for touch layouts */}
            <div className="child-bottom-zone h-1/6">
            </div>

        </div>
    );
};

export default ChildSessionPage;
