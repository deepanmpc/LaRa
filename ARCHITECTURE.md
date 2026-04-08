# LaRa Architecture Diagrams

Below are the architectural diagrams for the current version of the LaRa (Low-Cost Adaptive Robotic-AI Assistant) system, capturing all active engines, pipelines, and subsystems, rendered using Mermaid.

## Figure 1: LaRa System Overview (Full Block Diagram)
```mermaid
graph TD
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,color:#fff,rx:8px,ry:8px;
    classDef backend fill:#10b981,stroke:#047857,color:#fff,rx:8px,ry:8px;
    classDef ai fill:#6366f1,stroke:#4338ca,color:#fff,rx:8px,ry:8px;
    classDef db fill:#f59e0b,stroke:#b45309,color:#fff,rx:8px,ry:8px;

    User[Child/Clinician] --> Dash[LaRa Dashboard Frontend<br>React / Recharts]:::frontend
    Dash <-- REST / WebSockets --> Spring[Spring Boot API<br>Clinical Backend]:::backend
    
    Spring <--> core[Python AI Core<br>src/core]:::ai
    
    subgraph Python AI Engine
        core --> vision[Vision Perception<br>Face / Gaze / Pose]:::ai
        core --> voice[Audio Pipeline<br>Whisper / TTS]:::ai
        core --> llm[Agentric LLM<br>Ollama / AgentricAI_TLM]:::ai
        core --> session[Session & State<br>FSM / Streaks]:::ai
        core --> memory[Memory Subsystem<br>User / Vector]:::ai
    end
    
    memory <--> pg[PostgreSQL / SQLite<br>User Data]:::db
    memory <--> faiss[FAISS Vector Store<br>Semantic Memory]:::db
    Spring <--> pg
```

## Figure 2: Vision Perception Pipeline
```mermaid
graph TD
    classDef input fill:#ef4444,color:#fff;
    classDef process fill:#8b5cf6,color:#fff;
    classDef state fill:#14b8a6,color:#fff;

    Cam[Camera Module]:::input --> Det[Detection Engine<br>MediaPipe / Haar]:::process
    Det --> |Face/Pose Data| Track[Tracking & Feature Extraction]:::process
    
    Track --> Gaze{Gaze Direction?}:::process
    Gaze -->|Looking at Screen| Foc(FOCUSED):::state
    Gaze -->|Looking Away| Dist(DISTRACTED):::state
    Gaze -->|No Face| Abs(ABSENT):::state
    
    Foc --> Calc[Engagement Score Calculation]:::process
    Dist --> Calc
    Abs --> Calc
    
    Calc --> |Avg Score, Duration| Ses[Session State Update]:::state
```

## Figure 3: Session State Machine (FSM)
```mermaid
stateDiagram-v2
    [*] --> Neutral : Start Session
    
    Neutral --> Frustrated : 2 Consecutive Frustrated Moods (Conf >= 0.6)
    Neutral --> Stable : 3 Consecutive Stable Moods (Conf >= 0.6)
    
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
    classDef segment fill:#374151,stroke:#9ca3af,color:#fff,rx:5px,ry:5px;
    
    P1["1. System Rules (Self)"]:::segment
    P2["2. Recovery Strategy"]:::segment
    P3["3. Reinforcement Style"]:::segment
    P4["4. Learning State (Memory/Pref)"]:::segment
    P5["5. Session Summary (Vision)"]:::segment
    P6["6. History Block (Last N Turns)"]:::segment
    P7["7. Live Input Block (User Text)"]:::segment
    
    subgraph Prompt Cache Manager
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
    classDef layer fill:#ec4899,color:#fff;
    classDef comp fill:#475569,color:#fff;
    
    subgraph Layer 3: Semantic Memory (Persisted Semantic)
        VectorDB[FAISS Vector Store]:::layer
        ChildPref[Child Preferences]:::layer
    end
    
    subgraph Layer 2: Episodic Memory (Persisted Context)
        TurnHist[Turn History Database]:::layer
        VisionHist[Vision/Timeline Database]:::layer
    end

    subgraph Layer 1: Working Memory (In-Memory Session)
        Ses[SessionState (RAM)]:::layer
        Streaks[Frustration/Stability Counters]:::comp
        Mood[Current Mood/Confidence]:::comp
        Ses --> Streaks
        Ses --> Mood
    end
    
    Layer1 --> |Timer Flush (2.0s)| Layer2
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
    classDef audio fill:#f97316,color:#fff;
    classDef visual fill:#8b5cf6,color:#fff;
    classDef fuse fill:#0ea5e9,color:#fff;

    A[Audio Input]:::audio --> Pitch[Pitch/Tempo Extraction]:::audio
    A --> Voc[Vocal Energy (RMS)]:::audio
    
    V[Video Input]:::visual --> FA[Face Expression Analysis]:::visual
    V --> Act[Activity/Gesture]:::visual
    
    Pitch --> Fuse{Multi-Modal Fusion}:::fuse
    Voc --> Fuse
    FA --> Fuse
    Act --> Fuse
    
    Fuse --> Conf{Confidence >= 0.6?}:::fuse
    Conf --> |Yes| Mood[Detected Mood: Happy/Sad/Frust/Neutral]
    Conf --> |No| Un[Unknown / Default Neutral]
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
    classDef ext fill:#1f2937,color:#fff;
    classDef svc fill:#2563eb,color:#fff;
    
    Client[Browser / Tablet]:::ext --> |HTTPS/WSS| Proxy[Nginx / API Gateway]:::svc
    
    Proxy --> React[Service 1: React Dashboard UI]:::svc
    Proxy --> Spring[Service 2: Spring Boot Backend]:::svc
    
    Spring --> Python[Service 3: Python AI Core]:::svc
    Python --> |WebRTC/gRPC| LocalAI[Local Inference Models]:::ext
    
    Spring --> DB[(Service 4: PostgreSQL + Redis + FAISS)]:::svc
    Python --> DB
```

## Figure 10: Engagement Scoring Algorithm Flowchart
```mermaid
flowchart TD
    Start[Capture Frame] --> Face{Face Detected?}
    Face -->|No| Sub[Score = 0, State = ABSENT]
    Face -->|Yes| Gaze{Gaze Vector toward Screen?}
    
    Gaze -->|Yes| Foc[State = FOCUSED]
    Gaze -->|No| Dist[State = DISTRACTED]
    
    Foc --> Base[Base Score = 80]
    Dist --> Base[Base Score = 40]
    
    Base --> Gesture{Positive Gesture Detected?}
    Gesture -->|Yes| Add[Add +20]
    Gesture -->|No| Keep[Keep Score]
    
    Add --> Final[Final Score for Frame]
    Keep --> Final
    Final --> Avg[Calculate 1min Moving Average]
```
