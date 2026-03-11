
# LaRa — Child Interaction Page Implementation Tasks
## Full Task & TODO Breakdown for Agents

Version: 1.0  
Scope: Child Interaction Page Only  
Stack: React + Vite Frontend  
Integration: Spring Boot Backend + Vision Microservice  
Mode: Fullscreen Kiosk Interface

---

# Implementation Goal

Implement the **Child Interaction Page** used during LaRa learning sessions.

This page runs on the device in front of the child and must be:

• Fullscreen  
• Distraction-free  
• Voice-driven  
• Touch friendly  
• Simple and predictable  

This interface **does not include analytics or dashboard features**.

---

# System Context

Already existing:

• Session page for parents  
• Vision perception microservice  
• Backend session APIs  
• Activity content stored in database  
• Session orchestration service  

This task only implements the **child UI layer**.

---

# Task Execution Order

Tasks must be completed **in order**.

```
Phase 1 — Routing and Page Shell
Phase 2 — Layout Zones
Phase 3 — Lara Avatar System
Phase 4 — Activity Engine
Phase 5 — Activity Components
Phase 6 — Response Handling
Phase 7 — Celebration System
Phase 8 — Attention Recovery
Phase 9 — Session Completion
Phase 10 — Visual Polish
```

---

# PHASE 1 — ROUTING

## Task 1.1 — Add Child Session Route

File to edit

```
src/App.jsx
```

Add route:

```jsx
<Route
 path="/child-session/:childId/:sessionUuid"
 element={<ChildSessionPage />}
/>
```

Requirements

• Route must not require authentication  
• Page must open without dashboard layout  
• No sidebar  
• No navigation  

Done when:

Child page opens directly in browser.

---

# PHASE 2 — PAGE SHELL

## Task 2.1 — Create Child Session Page

Create file

```
src/pages/ChildSessionPage.jsx
```

State required

```
sessionType
activities
currentActivityIndex
speechText
laraState
celebration
```

Base structure

```jsx
<div className="child-session-page">

<div className="child-top-zone">
<LaraAvatar state={laraState}/>
<div className="speech-bubble">{speechText}</div>
</div>

<div className="child-mid-zone">
<ActivityArea/>
</div>

<div className="child-bottom-zone">
</div>

</div>
```

---

# PHASE 3 — LARA AVATAR

## Task 3.1 — Create Avatar Component

Create file

```
src/components/child/LaraAvatar.jsx
```

Avatar states

```
idle
speaking
waiting
celebrating
```

Animations required

Idle

```
gentle breathing animation
```

Speaking

```
mouth movement
```

Waiting

```
soft glowing pulse
```

Celebrating

```
bounce animation
sparkle
```

Avatar size

```
120px
```

---

# PHASE 4 — ACTIVITY ENGINE

## Task 4.1 — Create Activity Router

Create file

```
src/components/child/ActivityArea.jsx
```

Switch based on sessionType.

Supported session types

```
VOCABULARY
STORY_SEQUENCING
SOCIAL_SCENARIOS
MATH_BASICS
FREE_PLAY
```

Example logic

```javascript
switch(sessionType){
 case "VOCABULARY":
  return <VocabularyActivity />

 case "STORY_SEQUENCING":
  return <StorySequencingActivity />

 case "SOCIAL_SCENARIOS":
  return <SocialScenariosActivity />

 case "MATH_BASICS":
  return <MathBasicsActivity />

 case "FREE_PLAY":
  return <FreePlayActivity />
}
```

---

# PHASE 5 — ACTIVITY COMPONENTS

Create directory

```
src/components/child/activities
```

---

## Task 5.1 Vocabulary Activity

Create

```
VocabularyActivity.jsx
```

Layout

```
image
word label
answer buttons
```

Example UI

```
   🍎
  Apple

[Apple] [Banana] [Orange]
```

Buttons must be

```
large
touch friendly
min height 70px
```

---

## Task 5.2 Story Sequencing

Create

```
StorySequencingActivity.jsx
```

Display

```
multiple scene cards
```

Child taps cards in order.

Numbers appear

```
1
2
3
```

After last selection

```
submit answer
```

---

## Task 5.3 Social Scenarios

Create

```
SocialScenariosActivity.jsx
```

Display

```
scene image
emotion choices
```

Emotion buttons

```
😊 Happy
😢 Sad
😠 Angry
😮 Surprised
```

Large emoji buttons.

---

## Task 5.4 Math Basics

Create

```
MathBasicsActivity.jsx
```

Display equation visually

Example

```
🍎 🍎 🍎 + 🍎 🍎
```

Answer buttons

```
[3] [4] [5]
```

Square buttons.

---

## Task 5.5 Free Play

Create

```
FreePlayActivity.jsx
```

Display

```
Lara avatar
speech bubble
microphone button
```

Mic button

```
large circle
pulse animation
```

Important

This UI **does not capture audio**.

Audio handled by backend STT pipeline.

---

# PHASE 6 — RESPONSE HANDLING

## Task 6.1 Answer Submission

Send answer to backend

```
POST /api/child-activity/answer
```

Request

```
activityId
answer
```

Response

```
correct
correctAnswer
```

Correct answer triggers celebration.

Wrong answer triggers retry.

---

# PHASE 7 — CELEBRATION SYSTEM

## Task 7.1 Celebration Overlay

Create

```
src/components/child/CelebrationOverlay.jsx
```

Overlay behavior

• Appears after correct answer  
• Shows star or confetti animation  
• Displays praise message

Example message

```
Great job!
```

Overlay duration

```
2 seconds
```

---

# PHASE 8 — ATTENTION RECOVERY

When vision system detects distraction:

LaRa performs wave animation.

Speech example

```
Hey! I'm over here 👋
```

When child leaves frame:

• Activity pauses  
• Screen dims slightly  

Speech example

```
I'll wait for you.
```

When child returns:

```
Welcome back!
```

Resume activity.

---

# PHASE 9 — SESSION COMPLETION

When session ends:

Display celebration screen.

Example UI

```
🎉 Great job today!
```

LaRa speech

```
I'm proud of you!
```

Then return to idle screen.

---

# PHASE 10 — VISUAL POLISH

Design rules

• One activity at a time  
• Large buttons  
• No clutter  
• Smooth transitions  
• Consistent layout  

The child must **never see**:

```
scores
percentages
difficulty levels
timers
error messages
menus
navigation
```

Those are reserved for the parent dashboard.

---

# Final Flow

```
Session starts
      ↓
LaRa greeting
      ↓
Activity appears
      ↓
Child responds
      ↓
Praise animation
      ↓
Next activity
      ↓
Repeat
      ↓
Session celebration
```
