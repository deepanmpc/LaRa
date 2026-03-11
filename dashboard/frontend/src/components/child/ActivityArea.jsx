import React from 'react';

// Activity Component Stubs
import VocabularyActivity from './activities/VocabularyActivity';
import StorySequencingActivity from './activities/StorySequencingActivity';
import SocialScenariosActivity from './activities/SocialScenariosActivity';
import MathBasicsActivity from './activities/MathBasicsActivity';
import FreePlayActivity from './activities/FreePlayActivity';

const ActivityArea = ({ sessionType, onAnswer }) => {
    
    // Switch based on sessionType (Phase 4 Spec)
    switch(sessionType) {
        case "VOCABULARY":
            return <VocabularyActivity onAnswer={onAnswer} />;
            
        case "STORY_SEQUENCING":
            return <StorySequencingActivity onAnswer={onAnswer} />;
            
        case "SOCIAL_SCENARIOS":
            return <SocialScenariosActivity onAnswer={onAnswer} />;
            
        case "MATH_BASICS":
            return <MathBasicsActivity onAnswer={onAnswer} />;
            
        case "FREE_PLAY":
            return <FreePlayActivity />;
            
        default:
            return (
                <div className="text-3xl text-slate-400 font-light">
                    Loading activity...
                </div>
            );
    }
};

export default ActivityArea;
