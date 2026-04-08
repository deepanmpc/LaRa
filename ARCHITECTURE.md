# LaRa Architecture Diagrams (Detailed View)

Below are the detailed architectural and data-flow diagrams for the LaRa system. These extend the high-level overviews to include specific technical protocols, backend services, ports, memory persistence layers, and internal configuration details.

## Figure 1: LaRa System Overview (Full Data-Flow Diagram)
```mermaid
graph TD
    User["Child/Clinician User"] --> UI["React / Vite Dashboard (Port 5173)"]
    
    UI <-->|REST / JSON| SpringAPI["Spring Boot Backend (Port 8080)
    DashboardAPIController / ClinicianController"]
    
    UI <-->|WebSocket: Session Control| WSBridge[\"WS Bridge (Port 8765)
    src/bridge/ws_server.py"/]
    
    SpringAPI <-->|SQL Sync| Postgres[("User/Clinical Data
    PostgreSQL / SQLite")]
    
    WSBridge <--> MainDaemon["Main Python Pipeline (run.sh)
    src/main.py"]
    
    subgraph CoreAI ["Python AI Engine (Gated EventBus Loop)"]
        MainDaemon --> EventBus["EventBus (Pub/Sub)
        SESSION_STARTED / COMPLETED"]
        MainDaemon --> SessionMGR["Session & State Manager
        FSM, Counters"]
        MainDaemon --> LLM["Agentric LLM Controller
        Ollama/AgentricAI_TLM"]
        MainDaemon --> AudioPipe["Audio Pipeline
        Whisper (ASR) / TTS"]
        MainDaemon --> VisionBridge["VisionBridgeService"]
    end
    
    VisionBridge <-->|REST Polling 2Hz| VisionAPI["Vision Perception API
    FastAPI / Uvicorn (Port 8001)"]
    
    SessionMGR <--> DB_Sync["SessionDBSync Layer"]
    DB_Sync <--> Postgres
    LLM <--> FAISS[("FAISS Vector DB
    Semantic Memory")]
```

## Figure 2: Vision Perception Pipeline (FastAPI to Main Sync)
```mermaid
graph TD
    Cam["Hardware Camera (15-30 FPS)"] --> Uvicorn["FastAPI App (Port 8001)"]
    
    subgraph VisionService ["FastAPI Vision Worker"]
        Uvicorn --> MediaPipe["MediaPipe FaceMesh/Pose"]
        MediaPipe --> |"Landmarks"| Tracker["Spatial Tracker"]
        
        Tracker --> Gaze{"Gaze Vector
        Intersection"}
        Gaze -->|Screen| FOC["FOCUSED"]
        Gaze -->|Away| DIST["DISTRACTED"]
        Gaze -->|None| ABS["ABSENT"]
        
        FOC --> BaseS["Score: 80-100"]
        DIST --> BaseS2["Score: 20-40"]
        ABS --> BaseS3["Score: 0"]
        
        BaseS --> SyncBuf["Rolling JSON Buffer"]
        BaseS2 --> SyncBuf
        BaseS3 --> SyncBuf
    end
    
    SyncBuf <-->|GET /analytics (0.5s Interval)| VisionBridge[\"Main Pipeline Vision Bridge"/]
    
    VisionBridge --> Aggregator["60-second Sliding Window
    Calculate Avg Engagement (120 samples)"]
    Aggregator -->|Publish: ENGAGEMENT_MINUTE_SYNC| EventBus["Core Event Bus"]
```

## Figure 3: Session State Machine (FSM & Configuration)
```mermaid
stateDiagram-v2
    [*] --> Neutral : UI Trigger (session_start)
    
    Neutral --> Frustrated : 2 Consecutive 'Frustrated/Sad'\n[Conf >= 0.6]
    Neutral --> Stable : 3 Consecutive 'Happy/Neutral'\n[Conf >= 0.6]
    
    state Frustrated {
        [*] --> DecreaseDifficulty : Delta -1\nClamp [1, 5]
        DecreaseDifficulty --> LockDifficulty : locked_turns = 2
    }
    
    state Stable {
        [*] --> IncreaseDifficulty : Delta +1\nClamp [1, 5]
        IncreaseDifficulty --> LockDifficulty : locked_turns = 2
    }
    
    LockDifficulty --> LockDifficulty : Turn Count++
    LockDifficulty --> Neutral : Turn Count == 2
    
    Frustrated --> CheckTTL : Idle > TTL Hour
    Stable --> CheckTTL : Idle > TTL Hour
    Neutral --> CheckTTL : Idle > TTL Hour
    
    CheckTTL --> [*] : Terminate/Flush DB (session_stop)
```

## Figure 4: 7-Segment Agentric Prompt Architecture
```mermaid
flowchart TD
    Config["CONFIG.llm
    Top-p: 0.85, Top-k: 40
    Num-ctx: 1024, Temp: 0.15"] -.-> OllamaAPI
    
    subgraph Segments ["Memory Retrieval & Prompt Blocks"]
        Sys["1. System Prompt (No Sarcasm/Metaphors)"]
        Strat["2. Recovery Strategy Block"]
        Style["3. Reinforcement Style"]
        Mem["4. Learning State (from FAISS)"]
        Vis["5. Vision Session Summary"]
        Hist["6. Conversation History (Sliding Compress)"]
        Live["7. Current Turn Input: 'User says...'"]
    end
    
    Sys --> Cache["PromptCacheManager"]
    Strat --> Cache
    Style --> Cache
    Mem --> Cache
    Vis --> Cache
    Hist --> Cache
    Live --> Cache
    
    Cache --> |"Full Context String"| OllamaAPI["Local HTTP POST /api/generate
    Model: AgentricAI_TLM"]
    OllamaAPI --> |"Iterative Chunks (stream=True)"| Yield["Streaming TTS Yield"]
```

## Figure 5: Memory Architecture (3-Tier Layered Hierarchy)
```mermaid
graph LR
    subgraph L3 ["Layer 3: Semantic Memory (Disk/DB)"]
        FAISS["FAISS Index (Embeddings)"]
        SqlConfig["SQLite Schema / Policies"]
        ChildProf["Persistent Child Profiles"]
    end
    
    subgraph L2 ["Layer 2: Episodic Memory (Disk/JSON)"]
        DBSync["SessionDBSync Manager"]
        TurnJSON["Turn History JSON (session_id_state)"]
        Timeline["Timeline Metrics (1 min bins)"]
    end

    subgraph L1 ["Layer 1: Working Memory (RAM)"]
        SessionObj["SessionState Dataclass"]
        TurnCnt["Turn Counters & Emotion Streaks"]
        LockTimers["Difficulty Lock Timers"]
        
        SessionObj --> TurnCnt
        SessionObj --> LockTimers
    end
    
    L1 -->|"Debounced Save Trigger (2.0s timeout)"| L2
    L2 <--|"Metadata & Aggregates Extractions"| L3
```

## Figure 6: Latency Breakdown Chart 
```mermaid
xychart-beta
    title "End-to-End Latency Target Breakdown (ms)"
    x-axis ["VAD Detection", "Whisper Transcribe", "Vision Sync (Async)", "LLM Generation", "TTS Output", "Total Budget"]
    y-axis "Max Processing Latency Time (ms)" 0 --> 3500
    bar [150, 600, 50, 1500, 500, 2800]
```

## Figure 7: Emotion Detection Stack
```mermaid
graph TD
    Mic["Microphone Audio Stream"] --> VAD["WebRTC VAD (Mode 3)"]
    VAD --> Whisper["Whisper small.en Transcriber"]
    
    Whisper --> |"Text Transcript"| NLP["Sentiment Logic (Optional)"]
    Mic --> |"Raw Frames"| RMS["RMS Audio Energy"]
    
    Cam["Vision API Port 8001"] --> FACS["Face Action Unit Analysis"]
    Cam --> Pose["Pose & Restlessness"]
    
    NLP --> Fusion{"Multi-Modal Fusion Controller"}
    RMS --> Fusion
    FACS --> Fusion
    Pose --> Fusion
    
    Fusion --> Bayesian{"Bayesian Conf Check
    Score >= 0.60?"}
    Bayesian --> |"Yes"| MoodEmit["Emit: Detected_Mood (e.g., 'frustrated')"]
    Bayesian --> |"No"| Reg["Emit: 'unknown' (Trigger Recovery Block)"]
```

## Figure 8: Dashboard Architecture (Clinical + Family Interfaces)
```mermaid
mindmap
  root((React Vite UI))
    Clinical View (ClinicianDashboard.jsx)
      Data Fetching Layer
        DashboardAPIController (Spring Boot Endpoint)
      Components
        ClinicianStudentDetail Component
        ClinicalStudentSections Component
      Metrics Displayed
        Database Aggregated Empathy Stats
        Recharts Longitudinal Vision Analytics
    Family View (Parent Dashboard)
      Components
        Gamified Session Highlights
        Learning Progress Widgets
      Metrics Displayed
        Daily Difficulty Trajectories
        Daily Session Count / Total Duration
```

## Figure 9: Deployment Architecture (Hardware & Network Mapping)
```mermaid
graph TD
    subgraph Client ["Browser / Edge Device"]
        Vite["React Frontend SPA"] "--> HttpPort[Port: 5173]"
    end
    
    subgraph Spring ["Java Runtime"]
        Boot["Spring Boot Backend"] "--> ApiPort[Port: 8080]"
        Boot <--> |"JDBC / Hibernate"| DB
    end
    
    subgraph PyEnv ["Python Virtual Environment (.venv)"]
        Pipe["src/main.py Gated Pipeline"] "--> Ws[Port: 8765]"
        Pipe <--> EventBus["EventBus Manager"]
        Vis["src/vision_perception/app.py"] "--> Uvic[Port: 8001]"
    end
    
    subgraph DataStore ["Persistence Layer"]
        DB[("Postgres / SQLite
        port: 5432")]
        Vector[("FAISS Store")]
    end
    
    Client == "REST API" ==> Boot
    Client == "WebSocket" ==> Pipe
    Pipe == "REST API Polling" ==> Vis
```

## Figure 10: Engagement Scoring & Sync Flowchart
```mermaid
flowchart TD
    API["FastAPI captures Frame"] --> Haar{"Face MediaPipe / Haar?"}
    
    Haar -->|"No"| NullState["Attention = ABSENT\nScore = 0"]
    Haar -->|"Yes"| Gaze{"Eye Landmarks to Screen Intersect?"}
    
    Gaze -->|"Offset > Threshold"| Dist["Attention = DISTRACTED\nScore = 40"]
    Gaze -->|"Offset <= Threshold"| Foc["Attention = FOCUSED\nScore = 80"]
    
    NullState --> Emit["Store in Rolling Array"]
    Dist --> Gest{"Add Positive Gesture?"}
    Foc --> Gest
    
    Gest --> |"Yes (+20 limit)"| ModScore["Max Score 100"]
    Gest --> |"No"| BaseScore["Base Score"]
    
    ModScore --> Emit
    BaseScore --> Emit
    
    Emit -.-> |"Main Pipeline requests /analytics"| MainBuf["SessionState._vision_history"]
    MainBuf --> Time["_engagement_sync_loop (run every 60s)"]
    Time --> Calc["Calculate 1-Min Moving Average"]
    Calc --> DBPub["Publish to SQL/Stats Engine"]
```
