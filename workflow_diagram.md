# PROJECT NEXUS — Architecture & Workflow Diagram

**Autonomous Multi-Agent AI Problem Solver**  
*Developed by Pranav, AI & DE Branch*

---

## 1. Multi-Agent Orchestration Architecture

```mermaid
flowchart TD
    User([User Problem Statement / Voice Input]) --> START([START])
    START --> Planner["Supervisor / Dynamic Planner Agent<br/>(Task Decomposition & Queue Init)"]

    Planner --> Dispatcher{"Supervisor Dispatcher<br/>(Dynamic Routing Logic)"}

    Dispatcher -- "Human Checkpoint Enabled" --> HITL["Human Checkpoint (HITL)<br/>Approve / Edit Subtasks"]
    HITL --> Dispatcher

    Dispatcher -- "Research Subtask" --> Researcher["Web Researcher Agent<br/>(Tavily Search + Citations)"]
    Researcher --> Dispatcher

    Dispatcher -- "Quantitative Subtask" --> Analyst["Data Analyst Agent<br/>(Python Execution + Matplotlib Charts)"]
    Analyst --> Dispatcher

    Dispatcher -- "Subtasks Complete" --> Critic["Critic & Output Verifier Agent<br/>(Quality Scoring & Self-Reflection)"]

    Critic -- "Score < 75 or Objections Found" --> Revision["Critic Revision Loop<br/>(Bounded Max 2 Rounds)"]
    Revision --> Researcher

    Critic -- "Score >= 75 (Approved)" --> Writer["Report Writer & Synthesizer<br/>(Markdown Assembly + .docx Export)"]

    Writer --> Memory["ChromaDB Long-Term Memory<br/>(Vector Store Persistence)"]
    Memory --> END([END: Streamlit / Web UI Delivery])
```

---

## 2. Dynamic Supervisor & Fault Tolerance Flow

```mermaid
sequenceDiagram
    autonumber
    actor User as User / Operator
    participant Supervisor as Dynamic Supervisor (Planner)
    participant HITL as Human Checkpoint
    participant Researcher as Web Researcher
    participant Analyst as Data Analyst
    participant Critic as Critic Agent
    participant Writer as Report Writer
    participant Memory as ChromaDB Store

    User->>Supervisor: Complex Query / Problem
    Supervisor->>Supervisor: Decompose into N prioritized subtasks
    alt Auto-Approve Disabled
        Supervisor->>HITL: Request subtask approval
        HITL->>Supervisor: Approved plan
    end

    loop Dynamic Execution Loop
        Supervisor->>Researcher: Dispatch Research Subtask
        Researcher-->>Supervisor: Structured Findings + Citations
        Supervisor->>Analyst: Dispatch Quantitative Subtask
        Analyst-->>Supervisor: Data Insights + Generated Charts
    end

    Supervisor->>Critic: Submit findings for quality audit
    alt Quality Score < Threshold
        Critic->>Researcher: Target revision query
        Researcher-->>Critic: Revised findings
    end

    Critic->>Writer: Verified evidence bundle
    Writer->>Writer: Synthesize Markdown & Build .docx
    Writer->>Memory: Index session embeddings
    Writer->>User: Deliver interactive solution + .docx download
```

---

*Developed by Pranav, AI & DE Branch*
