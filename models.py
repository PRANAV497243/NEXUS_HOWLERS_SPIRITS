"""
PROJECT NEXUS — Autonomous Multi-Agent AI Problem Solver
Shared State and Data Models
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated, Any, List, Optional
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# ─────────────────────────────────────────────
# Pydantic Models for Structured Agent Outputs
# ─────────────────────────────────────────────

class SubQuestion(BaseModel):
    """A single subtask/sub-question dynamically assigned by the Planner/Supervisor."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    question: str
    agent: str = Field(description="Assigned specialized agent: 'researcher', 'analyst', 'critic', 'writer', 'execution'")
    tools_needed: list[str] = Field(default_factory=lambda: ["web_search"])
    priority: int = Field(default=1, ge=1, le=5)
    status: str = "pending"  # pending, in_progress, completed, failed
    dependencies: list[str] = Field(default_factory=list)
    output_summary: Optional[str] = None


class ResearchPlan(BaseModel):
    """Output of the Planner/Supervisor agent with dynamic decomposition."""
    original_question: str
    sub_questions: list[SubQuestion]
    approach_summary: str
    estimated_complexity: str = "medium"
    human_approved: bool = False


class Citation(BaseModel):
    """Source citation extracted during research."""
    title: str
    url: str
    snippet: str = ""
    date: str = ""
    relevance_score: float = 0.0


class ResearchFinding(BaseModel):
    """Output from the Web Researcher agent."""
    sub_question: str
    summary: str
    key_points: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    conflicts: list[str] = Field(default_factory=list)
    confidence: float = Field(default=0.8, ge=0.0, le=1.0)


class DataInsight(BaseModel):
    """Output from the Data Analyst / Code Execution agent."""
    sub_question: str
    analysis_summary: str
    data_points: list[dict[str, Any]] = Field(default_factory=list)
    chart_paths: list[str] = Field(default_factory=list)
    code_executed: str = ""
    methodology: str = ""


class CriticReview(BaseModel):
    """Output from the Critic Agent for quality verification and self-reflection."""
    score: float = Field(description="Quality score from 0 to 100", ge=0.0, le=100.0)
    is_approved: bool = False
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    objections: list[str] = Field(default_factory=list)
    revision_feedback: str = ""


class ReportSection(BaseModel):
    """A structured section of the final synthesized report."""
    title: str
    content: str
    citations: list[Citation] = Field(default_factory=list)
    confidence_score: float = 0.0


class FinalReport(BaseModel):
    """Final solution produced by the Writer agent."""
    title: str
    executive_summary: str
    sections: list[ReportSection] = Field(default_factory=list)
    conclusion: str = ""
    metadata: dict[str, Any] = Field(default_factory=dict)
    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    markdown: str = ""
    docx_path: Optional[str] = None


class AgentMessage(BaseModel):
    """Live activity update emitted by an agent."""
    agent: str
    message: str
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    msg_type: str = "info"  # info, thinking, success, warning, error


class ApprovalCheckpoint(BaseModel):
    """Data payload for Human-in-the-Loop decision point."""
    checkpoint_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    prompt: str
    sub_questions: list[SubQuestion]
    status: str = "pending"  # pending, approved, modified, rejected
    human_notes: Optional[str] = None


# ─────────────────────────────────────────────
# State Reducer Functions for LangGraph
# ─────────────────────────────────────────────

def merge_messages(existing: list[AgentMessage], new: list[AgentMessage]) -> list[AgentMessage]:
    return existing + new

def merge_findings(existing: list[ResearchFinding], new: list[ResearchFinding]) -> list[ResearchFinding]:
    return existing + new

def merge_insights(existing: list[DataInsight], new: list[DataInsight]) -> list[DataInsight]:
    return existing + new

def merge_errors(existing: list[str], new: list[str]) -> list[str]:
    return existing + new

def merge_history(existing: list[str], new: list[str]) -> list[str]:
    return existing + new

def keep_last_agent(existing: str, new: str) -> str:
    return new if new else existing


# ─────────────────────────────────────────────
# Master LangGraph Shared State
# ─────────────────────────────────────────────

class ResearchState(TypedDict):
    """The shared state flowing through PROJECT NEXUS orchestration."""
    query: str
    research_plan: ResearchPlan | None
    sub_questions: list[SubQuestion]
    pending_subtasks: list[SubQuestion]
    active_subtask: SubQuestion | None
    findings: Annotated[list[ResearchFinding], merge_findings]
    data_insights: Annotated[list[DataInsight], merge_insights]
    critic_reviews: list[CriticReview]
    critic_objections: list[str]
    revision_count: int
    human_approved: bool
    auto_approve_plan: bool
    final_report: FinalReport | None
    agent_messages: Annotated[list[AgentMessage], merge_messages]
    current_agent: Annotated[str, keep_last_agent]
    errors: Annotated[list[str], merge_errors]
    routing_history: Annotated[list[str], merge_history]
    docx_path: str | None
    session_id: str
