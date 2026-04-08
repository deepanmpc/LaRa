# LaRa Architecture Diagrams

Below are the architectural diagrams for the current version of the LaRa (Low-Cost Adaptive Robotic-AI Assistant) system, capturing all active engines, pipelines, and subsystems, rendered using Mermaid.

## Figure 1: LaRa System Overview (Full Block Diagram)
```mermaid
graph TD
    User[Child/Clinician] --> Dash[LaRa Dashboard Frontend - React/Recharts]
    Dash <-- REST / WebSockets --> Spring[Spring Boot API - Clinical Backend]
    
    Spring <--> core[Python AI Core - src/core]
    
    subgraph Python_AI_Engine [Python AI Engine]
        core --> vision[Vision Perception - Face/Gaze/Pose]
        core --> voice[Audio Pipeline - Whisper/TTS]
        core --> llm[Agentric LLM - Ollama / AgentricAI_TLM]
        core --> session[Session & State - FSM/Streaks]
        core --> memory[Memory Subsystem - User/Vector]
    end
    
    memory <--> pg[PostgreSQL / SQLite - User Data]
    memory <--> faiss[FAISS Vector Store - Semantic Memory]
    Spring <--> pg
```

## Figure 2: Vision Perception Pipeline
```mermaid
graph TD
    Cam[Camera Module] --> Det[Detection Engine - MediaPipe/Haar]
    Det --> |Face/Pose Data| Track[Tracking & Feature Extraction]
    
    Track --> Gaze{"Gaze Direction?"}
    Gaze -->|Looking at Screen| Foc(FOCUSED)
    Gaze -->|Looking Away| Dist(DISTRACTED)
    Gaze -->|No Face| Abs(ABSENT)
    
    Foc --> Calc[Engagement Score Calculation]
    Dist --> Calc
    Abs --> Calc
    
    Calc --> |Avg Score, Duration| Ses[Session State Update]
```

## Figure 3: Session State Machine (FSM)
```mermaid
stateDiagram-v2
    [*] --> Neutral : Start Session
    
    Neutral --> Frustrated : 2 Consecutive Frustrated Moods
    Neutral --> Stable : 3 Consecutive Stable Moods
    
    state Frustrated {
        [*] --> DecreaseDifficulty
        DecreaseDifficulty --> LockDifficulty : Lock for N Turns
    }
    
    state Stable {
        [*] --> IncreaseDifficulty
        IncreaseDifficulty --> LockDifficulty : Lock for N Turns
    }
    
    LockDifficulty --> Neutral : Lock Expired
    
    Frustrated --> Expired : > 24 Hours
    Stable --> Expired : > 24 Hours
    Neutral --> Expired : > 24 Hours
    
    Expired --> [*] : Reset Session
```

## Figure 4: 7-Segment Prompt Architecture
```mermaid
flowchart TD
    P1["1. System Rules (Self)"]
    P2["2. Recovery Strategy"]
    P3["3. Reinforcement Style"]
    P4["4. Learning State (Memory/Pref)"]
    P5["5. Session Summary (Vision)"]
    P6["6. History Block (Last N Turns)"]
    P7["7. Live Input Block (User Text)"]
    
    subgraph PromptManager [Prompt Cache Manager]
        P1 --> Cache[Assemble 7-Segment Prompt]
        P2 --> Cache
        P3 --> Cache
        P4 --> Cache
        P5 --> Cache
        P6 --> Cache
        P7 --> Cache
    end
    
    Cache --> LLM[AgentricAI_TLM / Local Ollama]
```

## Figure 5: Memory Architecture (3 Layers)
```mermaid
graph LR
    subgraph Layer3 ["Layer 3: Semantic Memory (Persisted Semantic)"]
        VectorDB[FAISS Vector Store]
        ChildPref[Child Preferences]
    end
    
    subgraph Layer2 ["Layer 2: Episodic Memory (Persisted Context)"]
        TurnHist[Turn History Database]
        VisionHist[Vision/Timeline Database]
    end

    subgraph Layer1 ["Layer 1: Working Memory (In-Memory Session)"]
        Ses["SessionState (RAM)"]
        Streaks["Frustration/Stability Counters"]
        Mood["Current Mood/Confidence"]
        Ses --> Streaks
        Ses --> Mood
    end
    
    Layer1 --> |Timer Flush 2.0s| Layer2
    Layer2 --> |Metadata Extract| Layer3
```

## Figure 6: Latency Breakdown Chart (Bar Chart)
```mermaid
xychart-beta
    title "End-to-End Latency Breakdown (ms)"
    x-axis ["Wake Word", "VAD+Audio", "Whisper ASR", "Prompt Build", "LLM Inference", "TTS Gen"]
    y-axis "Latency (ms)" 0 --> 3000
    bar [150, 450, 800, 50, 1500, 600]
```

## Figure 7: Emotion Detection Pipeline
```mermaid
graph TD
    A[Audio Input] --> Pitch["Pitch/Tempo Extraction"]
    A --> Voc["Vocal Energy (RMS)"]
    
    V[Video Input] --> FA["Face Expression Analysis"]
    V --> Act["Activity/Gesture"]
    
    Pitch --> Fuse{"Multi-Modal Fusion"}
    Voc --> Fuse
    FA --> Fuse
    Act --> Fuse
    
    Fuse --> Conf{"Confidence >= 0.6?"}
    Conf --> |Yes| Mood["Detected Mood: Happy/Sad/Frust/Neutral"]
    Conf --> |No| Un["Unknown / Default Neutral"]
```

## Figure 8: Dashboard Wireframe (Clinical + Family)
```mermaid
mindmap
  root((LaRa Dashboard))
    Clinical View
      Longitudinal Charts Recharts
      Aggregated Empathy Scores
      Behavioral Milestones
      Detailed Session Timelines
    Family View
      Recent Session Overviews
      Learning Highlights
      Difficulty Trajectories
      Daily Engagement Trends
```

## Figure 9: Deployment Architecture (4 Services)
```mermaid
graph TD
    Client[Browser / Tablet] --> |HTTPS/WSS| Proxy[Nginx / API Gateway]
    
    Proxy --> React[Service 1: React Dashboard UI]
    Proxy --> Spring[Service 2: Spring Boot Backend]
    
    Spring --> Python[Service 3: Python AI Core]
    Python --> |WebRTC/gRPC| LocalAI[Local Inference Models]
    
    Spring --> DB[(Service 4: PostgreSQL + Redis + FAISS)]
    Python --> DB
```

## Figure 10: Engagement Scoring Algorithm Flowchart
```mermaid
flowchart TD
    Start[Capture Frame] --> Face{"Face Detected?"}
    Face -->|No| Sub["Score = 0, State = ABSENT"]
    Face -->|Yes| Gaze{"Gaze Vector toward Screen?"}
    
    Gaze -->|Yes| Foc[State = FOCUSED]
    Gaze -->|No| Dist[State = DISTRACTED]
    
    Foc --> Base80["Base Score = 80"]
    Dist --> Base40["Base Score = 40"]
    
    Base80 --> Gesture{"Positive Gesture Detected?"}
    Base40 --> Gesture
    
    Gesture -->|Yes| Add["Add +20"]
    Gesture -->|No| Keep["Keep Score"]
    
    Add --> Final[Final Score for Frame]
    Keep --> Final
    Final --> Avg[Calculate 1min Moving Average]
```
