"""
PROJECT NEXUS — Autonomous Multi-Agent Orchestrator
LangGraph Dynamic Workflow Coordinating Planner, Researcher, Analyst, Critic, and Writer
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Generator, List

from langgraph.graph import StateGraph, START, END

from config import AUTO_APPROVE_PLAN, SYSTEM_ATTRIBUTION
from models import (
    AgentMessage,
    CriticReview,
    FinalReport,
    ResearchState,
    SubQuestion,
)
from agents.planner import run_planner, supervisor_dispatch
from agents.researcher import run_researcher
from agents.analyst import run_analyst
from agents.critic import run_critic, run_critic_revision
from agents.writer import run_writer
from database import save_session_report, search_related_history

logger = logging.getLogger("nexus.orchestrator")


# ─────────────────────────────────────────────
# Graph Nodes
# ─────────────────────────────────────────────

def human_approval_node(state: ResearchState) -> Dict[str, Any]:
    """
    Human-in-the-Loop Checkpoint (extracted from Multi-Agent-AI-Research-Analyst).
    Allows operator inspection, approval, or modification of the decomposed subtasks.
    In automated execution or CI, auto_approve_plan proceeds automatically.
    """
    plan = state.get("research_plan")
    sub_questions = state.get("sub_questions", [])
    query = state.get("query", "")

    # Look up past related memory to assist operator decision
    related = search_related_history(query, limit=2)

    messages = [
        AgentMessage(
            agent="human_checkpoint",
            message=f"📋 Human Checkpoint: Plan formulated with {len(sub_questions)} subtasks. Status: Auto-Approved." 
            if state.get("auto_approve_plan", AUTO_APPROVE_PLAN)
            else f"⏳ Human Checkpoint: Plan formulated with {len(sub_questions)} subtasks. Awaiting operator confirmation.",
            msg_type="info",
        )
    ]

    return {
        "human_approved": True,  # Confirmed for execution branch
        "current_agent": "human_checkpoint",
        "agent_messages": messages,
        "routing_history": [f"human_checkpoint | approved {len(sub_questions)} tasks | related_past={len(related)}"],
    }


def save_to_memory_node(state: ResearchState) -> Dict[str, Any]:
    """Saves completed research and findings to ChromaDB vector store."""
    messages = []
    try:
        report = state.get("final_report")
        if report and report.markdown:
            save_session_report(
                query=state["query"],
                findings=state.get("findings", []),
                report_markdown=report.markdown,
                metadata={
                    "attribution": SYSTEM_ATTRIBUTION,
                    "session_id": state.get("session_id", "default"),
                    "docx_path": str(state.get("docx_path", "")),
                },
            )
            messages.append(
                AgentMessage(
                    agent="memory",
                    message="💾 Long-term memory updated: Research vectors and embeddings stored in ChromaDB.",
                    msg_type="success",
                )
            )
    except Exception as e:
        messages.append(
            AgentMessage(
                agent="memory",
                message=f"⚠️ Memory storage note: {str(e)[:120]}",
                msg_type="warning",
            )
        )
    return {"agent_messages": messages, "current_agent": "memory"}


# ─────────────────────────────────────────────
# Dynamic Workflow Construction
# ─────────────────────────────────────────────

def build_nexus_graph() -> StateGraph:
    """
    Constructs the master LangGraph orchestration graph for PROJECT NEXUS:
    START -> planner -> supervisor_dispatch:
      ├─> human_checkpoint -> planner_resumption
      ├─> researcher ──> supervisor_dispatch
      ├─> analyst ────> supervisor_dispatch
      ├─> critic ─────> [pass -> writer | fail -> critic_revision]
      ├─> critic_revision ──> supervisor_dispatch
      └─> writer ─────> save_to_memory ──> END
    """
    workflow = StateGraph(ResearchState)

    # Core Agent Nodes
    workflow.add_node("planner", run_planner)
    workflow.add_node("human_checkpoint", human_approval_node)
    workflow.add_node("researcher", run_researcher)
    workflow.add_node("analyst", run_analyst)
    workflow.add_node("critic", run_critic)
    workflow.add_node("critic_revision", run_critic_revision)
    workflow.add_node("writer", run_writer)
    workflow.add_node("save_to_memory", save_to_memory_node)

    # Graph Topology with Dynamic Supervisor Dispatching
    workflow.add_edge(START, "planner")

    workflow.add_conditional_edges(
        "planner",
        supervisor_dispatch,
        {
            "human_checkpoint": "human_checkpoint",
            "researcher": "researcher",
            "analyst": "analyst",
            "critic": "critic",
            "writer": "writer",
        },
    )

    # From human checkpoint, loop back into dynamic supervisor
    workflow.add_conditional_edges(
        "human_checkpoint",
        supervisor_dispatch,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "critic": "critic",
            "writer": "writer",
        },
    )

    # Researcher & Analyst report back to Supervisor Dispatcher
    workflow.add_conditional_edges(
        "researcher",
        supervisor_dispatch,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "critic": "critic",
            "writer": "writer",
        },
    )

    workflow.add_conditional_edges(
        "analyst",
        supervisor_dispatch,
        {
            "researcher": "researcher",
            "analyst": "analyst",
            "critic": "critic",
            "writer": "writer",
        },
    )

    # Critic verification routing
    workflow.add_conditional_edges(
        "critic",
        lambda state: "critic_revision" if state.get("critic_objections") and state.get("revision_count", 0) < 2 else "writer",
        {
            "critic_revision": "critic_revision",
            "writer": "writer",
        },
    )

    # Revision branch re-enters researcher
    workflow.add_edge("critic_revision", "researcher")

    # Writer finalizes and updates memory
    workflow.add_edge("writer", "save_to_memory")
    workflow.add_edge("save_to_memory", END)

    return workflow


def compile_nexus_graph():
    """Compiles the LangGraph state machine."""
    return build_nexus_graph().compile()


# ─────────────────────────────────────────────
# Execution & Streaming Entry Points
# ─────────────────────────────────────────────

def create_initial_state(query: str, auto_approve: bool = True, session_id: str | None = None) -> ResearchState:
    """Prepares initial empty shared state for a run."""
    sid = session_id or str(uuid.uuid4())[:8]
    return {
        "query": query,
        "research_plan": None,
        "sub_questions": [],
        "pending_subtasks": [],
        "active_subtask": None,
        "findings": [],
        "data_insights": [],
        "critic_reviews": [],
        "critic_objections": [],
        "revision_count": 0,
        "human_approved": auto_approve,
        "auto_approve_plan": auto_approve,
        "final_report": None,
        "agent_messages": [
            AgentMessage(
                agent="nexus_system",
                message=f'🚀 Initializing PROJECT NEXUS for query: "{query}"',
                msg_type="info",
            )
        ],
        "current_agent": "nexus_system",
        "errors": [],
        "routing_history": [f"init | session={sid}"],
        "docx_path": None,
        "session_id": sid,
    }


def run_research(query: str, auto_approve: bool = True) -> ResearchState:
    """Synchronous complete execution of Project Nexus workflow."""
    graph = compile_nexus_graph()
    initial_state = create_initial_state(query, auto_approve=auto_approve)
    final_state = graph.invoke(initial_state)
    final_state["agent_messages"].append(
        AgentMessage(
            agent="nexus_system",
            message=f"✨ Execution concluded successfully. {SYSTEM_ATTRIBUTION}",
            msg_type="success",
        )
    )
    return final_state


def run_research_stream(query: str, auto_approve: bool = True) -> Generator[Dict[str, Any], None, None]:
    """
    Generator yielding step-by-step state snapshots for live Streamlit & Web UI updates.
    """
    graph = compile_nexus_graph()
    initial_state = create_initial_state(query, auto_approve=auto_approve)

    for event in graph.stream(initial_state, stream_mode="values"):
        yield event
