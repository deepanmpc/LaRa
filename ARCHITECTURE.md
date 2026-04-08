# LaRa Architecture Diagrams (2-Column Paper Optimized)

*Note: These diagrams have been strictly optimized for IEEE/ACM 2-column research paper formats. They exclusively use `TD` (Top-Down) layouts and stacked text labels to ensure they remain readable when scaled down to a ~3.5 inch column width.*

## Figure 1: LaRa System Overview
```mermaid
graph TD
    User["Child / Clinician"] --> UI["React UI<br>(Port 5173)"]
    
    UI <-->|REST| SpringAPI["Spring API<br>(Port 8080)"]
    UI <-->|WebSockets| WSBridge[\"WS Bridge<br>(Port 8765)"/]
    
    SpringAPI <--> Postgres[("SQL Data")]
    
    WSBridge <--> Main["Python Pipeline"]
    
    subgraph CoreAI ["AI Engine"]
        Main --> EventBus["EventBus"]
        Main --> Session["State FSM"]
        Main --> LLM["LLM Controller"]
        Main --> Audio["Audio Pipeline"]
        Main --> VisB["VisionBridge"]
    end
    
    VisB <-->|Polling| VisionAPI["Vision API<br>(Port 8001)"]
    Session <--> DB_Sync["DB Sync"]
    DB_Sync <--> Postgres
    LLM <--> FAISS[("FAISS Vector DB")]
```

## Figure 2: Vision Perception Pipeline
```mermaid
graph TD
    Cam["Camera (15-30 FPS)"] --> Uvicorn["FastAPI App"]
    
    subgraph VisionService ["Vision Worker"]
        Uvicorn --> MediaPipe["MediaPipe<br>FaceMesh"]
        MediaPipe --> Tracker["Spatial Tracker"]
        
        Tracker --> Gaze{"Gaze Vector"}
        Gaze -->|Screen| FOC["FOCUSED"]
        Gaze -->|Away| DIST["DISTRACTED"]
        Gaze -->|None| ABS["ABSENT"]
        
        FOC --> BaseS["Score: 80+"]
        DIST --> BaseS2["Score: 20-40"]
        ABS --> BaseS3["Score: 0"]
    end
    
    BaseS --> SyncBuf["Rolling Buffer"]
    BaseS2 --> SyncBuf
    BaseS3 --> SyncBuf
    
    SyncBuf <-->|GET /analytics| VisionBridge[\"Main Pipeline"/]
    VisionBridge --> Aggregator["1-Min Sliding Window<br>(120 samples)"]
    Aggregator -->|Publish Event| EventBus["Core Event Bus"]
```

## Figure 3: Session State Machine
```mermaid
stateDiagram-v2
    [*] --> Neutral : Start
    
    Neutral --> Frust : 2x Frustrated\n[Conf >= 0.6]
    Neutral --> Stable : 3x Stable\n[Conf >= 0.6]
    
    state "Frustrated State" as Frust {
        [*] --> DecDiff : Difficulty -1
        DecDiff --> LockFor2 : Lock 2 Turns
    }
    
    state "Stable State" as Stable {
        [*] --> IncDiff : Difficulty +1
        IncDiff --> LockFor2 : Lock 2 Turns
    }
    
    LockFor2 --> Neutral : Unlock
    
    Frust --> Sleep : Idle > TTL Hour
    Stable --> Sleep : Idle > TTL Hour
    Neutral --> Sleep : Idle > TTL Hour
    Sleep --> [*] : Terminate
```

## Figure 4: 7-Segment Prompt Architecture
```mermaid
flowchart TD
    Config["CONFIG.llm<br>p:0.85, k:40"] -.-> OllamaAPI
    
    subgraph Segments ["Context Blocks"]
        Sys["1. System Prompt"]
        Strat["2. Recovery Strategy"]
        Style["3. Reinforcement Style"]
        Mem["4. Learning State"]
        Vis["5. Vision Summary"]
        Hist["6. Turn History"]
        Live["7. Current Input"]
    end
    
    Sys --> Cache["PromptCacheManager"]
    Strat --> Cache
    Style --> Cache
    Mem --> Cache
    Vis --> Cache
    Hist --> Cache
    Live --> Cache
    
    Cache --> OllamaAPI["Local API<br>AgentricAI_TLM"]
```

## Figure 5: Memory Architecture
```mermaid
graph TD
    subgraph L123 ["Short-Term Working Memory"]
        L1["L1: Immediate Turn Buffer<br>Ephemeral, cleared per turn"]
        L2["L2: Rolling Session Buffer<br>Last 5 turns, 24h expiry"]
        L3["L3: Session Summary<br>Structured state sync<br>(Concept: counting | Diff: 2/5)"]
    end
    
    L1 --> L2 --> L3
    
    subgraph L4 ["Layer 4: Structured Session State"]
        L4Mem["RAM Only FSM<br>Expires Session End"]
    end
    
    L3 --> L4Mem
    
    subgraph L5 ["Layer 5: Long-Term Memory (SQLite)"]
        SQL["1. users (ID, Depth, TTS)<br>2. learning_progress (Mastery 0-5)<br>3. emotional_metrics (Weekly 0.95x decay)<br>4. child_preferences (Max 20, JSON)<br>5. reinforcement_metrics (Style success)"]
    end
    
    subgraph L6 ["Layer 6: Vector Memory"]
        Vec["ChromaDB<br>Optional, 90-day expiry"]
    end
    
    L4Mem -->|"Aggregated SQL Sync"| SQL
    L4Mem -.->|"Embeddings"| Vec
```

## Figure 6: Latency Breakdown Chart 
```mermaid
xychart-beta
    title "End-to-End Latency Target (ms)"
    x-axis ["VAD", "Whisper", "Vision", "LLM", "TTS"]
    y-axis "Max Latency (ms)" 0 --> 3500
    bar [150, 600, 50, 1500, 500]
```

## Figure 7: Emotion Detection Stack
```mermaid
graph TD
    Mic["Microphone"] --> Whisper["Whisper ASR"]
    Whisper --> NLP["Text Logic"]
    Mic --> RMS["Audio Energy"]
    
    Cam["Vision API"] --> FACS["Face Analysis"]
    Cam --> Pose["Pose Check"]
    
    NLP --> Fusion{"Modality Fusion"}
    RMS --> Fusion
    FACS --> Fusion
    Pose --> Fusion
    
    Fusion --> Bayesian{"Conf >= 0.60?"}
    Bayesian --> |"Yes"| Emit["Explicit Mood"]
    Bayesian --> |"No"| Reg["Fallback: 'unknown'"]
```

## Figure 8: Dashboard Architecture
```mermaid
mindmap
  root((React UI))
    Clinical View
      Longitudinal Charts
      Aggregated Empathy
      Behavioral Milestones
    Family View
      Recent Sessions
      Learning Progress
      Engagement Bins
```

## Figure 9: Deployment Architecture
```mermaid
graph TD
    Client["Browser"] --> Proxy["API Gateway"]
    Proxy --> React["React UI<br>Port 5173"]
    Proxy --> Boot["Spring Backend<br>Port 8080"]
    
    Boot <--> DB[("Postgres DB")]
    
    Proxy --> Pipe["Python Pipeline<br>Port 8765"]
    Pipe <--> Vis["Vision API<br>Port 8001"]
    
    Pipe <--> Vector[("FAISS Store")]
```

## Figure 10: Engagement Scoring Algorithm
```mermaid
flowchart TD
    API["FastAPI Frame"] --> Haar{"Face MediaPipe?"}
    
    Haar -->|"No"| NullState["ABSENT: 0"]
    Haar -->|"Yes"| Gaze{"Look at Screen?"}
    
    Gaze -->|"Offset > Threshold"| Dist["DISTRACTED: 40"]
    Gaze -->|"Offset <= Threshold"| Foc["FOCUSED: 80"]
    
    Dist --> Gest{"Positive Gesture?"}
    Foc --> Gest
    
    Gest --> |"Yes"| ModScore["Add +20"]
    Gest --> |"No"| BaseScore["Base"]
    
    NullState --> Emit["Add buffer"]
    ModScore --> Emit
    BaseScore --> Emit
    
    Emit -.-> |"Async Request"| main["SessionState"]
    main --> Time["Sync (60s loop)"]
    Time --> DBPub["Publish Average"]
```
