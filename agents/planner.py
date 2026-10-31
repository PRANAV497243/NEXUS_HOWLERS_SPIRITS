"""
PROJECT NEXUS — Dynamic Supervisor & Research Planner Agent
Decomposes Complex Problems into Subtasks and Dynamically Dispatches Agents
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from config import MAX_SUB_QUESTIONS, SYSTEM_ATTRIBUTION
from llm.client import generate, ModelTier
from models import AgentMessage, ResearchPlan, ResearchState, SubQuestion

logger = logging.getLogger("nexus.agents.planner")

PLANNER_SYSTEM_PROMPT = f"""You are the Dynamic Supervisor & Planning Agent of PROJECT NEXUS ({SYSTEM_ATTRIBUTION}).
Your role:
1. Deeply comprehend the user's objective and identify the root problem.
2. Decompose the request into up to {{max_sub_questions}} logically sequenced, non-overlapping subtasks.
3. Assign each subtask to the most capable specialized agent:
   - "researcher": for web search, empirical facts, documentation, background, and qualitative evidence.
   - "analyst": for numerical data, statistical trends, financial metrics, and Python chart generation.
   - "critic": for adversarial verification, cross-checking conflicting claims, and quality auditing.
4. Define dependencies, tools required ("web_search", "code_execution"), and priority (1 = highest).

You MUST respond strictly with a valid JSON object matching this schema:
{{{{
  "original_question": "the original user query",
  "approach_summary": "strategic explanation of problem breakdown",
  "estimated_complexity": "low" | "medium" | "high",
  "sub_questions": [
    {{{{
      "id": "task_1",
      "question": "clear, specific subtask instruction",
      "agent": "researcher" | "analyst",
      "tools_needed": ["web_search"],
      "priority": 1,
      "dependencies": []
    }}}}
  ]
}}}}
"""


def run_planner(state: ResearchState) -> Dict[str, Any]:
    """Plans research and initializes dynamic task queue."""
    query = state.get("query", "")
    messages = [
        AgentMessage(agent="planner", message=f'🧠 Supervisor analyzing objective: "{query}"', msg_type="thinking")
    ]

    prompt = query
    response_text = generate(
        prompt=prompt,
        system=PLANNER_SYSTEM_PROMPT.format(max_sub_questions=MAX_SUB_QUESTIONS),
        tier=ModelTier.STRONG,
    )

    try:
        clean_text = response_text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.startswith("```"):
            clean_text = clean_text[3:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        data = json.loads(clean_text)
    except Exception as e:
        logger.warning(f"Planner JSON parsing failed: {e}. Generating default decomposition.")
        data = {
            "original_question": query,
            "approach_summary": "Systematic breakdown covering background research, quantitative data analysis, and comparative review.",
            "estimated_complexity": "medium",
            "sub_questions": [
                {
                    "id": "task_1",
                    "question": f"Foundational background, key entities, and core mechanisms of: {query}",
                    "agent": "researcher",
                    "tools_needed": ["web_search"],
                    "priority": 1,
                    "dependencies": []
                },
                {
                    "id": "task_2",
                    "question": f"Statistical benchmarks, market trends, and data analysis for: {query}",
                    "agent": "analyst",
                    "tools_needed": ["web_search", "code_execution"],
                    "priority": 2,
                    "dependencies": ["task_1"]
                },
                {
                    "id": "task_3",
                    "question": f"Critical perspectives, limitations, and future implications for: {query}",
                    "agent": "researcher",
                    "tools_needed": ["web_search"],
                    "priority": 3,
                    "dependencies": ["task_1"]
                }
            ]
        }

    sub_questions: List[SubQuestion] = []
    for sq in data.get("sub_questions", []):
        sub_questions.append(
            SubQuestion(
                id=sq.get("id", f"task_{len(sub_questions)+1}"),
                question=sq.get("question", ""),
                agent=sq.get("agent", "researcher"),
                tools_needed=sq.get("tools_needed", ["web_search"]),
                priority=int(sq.get("priority", 1)),
                status="pending",
                dependencies=sq.get("dependencies", []),
            )
        )

    plan = ResearchPlan(
        original_question=query,
        sub_questions=sub_questions,
        approach_summary=data.get("approach_summary", ""),
        estimated_complexity=data.get("estimated_complexity", "medium"),
        human_approved=state.get("auto_approve_plan", False),
    )

    messages.append(
        AgentMessage(
            agent="planner",
            message=f"🎯 Decomposition complete: Created {len(sub_questions)} dynamic subtasks across specialized agents.",
            msg_type="success",
        )
    )

    return {
        "research_plan": plan,
        "sub_questions": sub_questions,
        "pending_subtasks": list(sub_questions),
        "agent_messages": messages,
        "current_agent": "planner",
        "routing_history": [f"planner | decomposed into {len(sub_questions)} subtasks"],
    }


def supervisor_dispatch(state: ResearchState) -> str:
    """
    Dynamic Supervisor Router (adapted from open_deep_research).
    Determines next node dynamically based on pending subtasks and critique state:
    - If Human Approval is required and not granted -> 'human_checkpoint'
    - If there are pending researcher tasks -> 'researcher'
    - If there are pending analyst tasks -> 'analyst'
    - If findings exist and critic has not reviewed -> 'critic'
    - If critic rejected and revision needed -> 'critic_revision'
    - If all subtasks and verification satisfied -> 'writer'
    """
    # 1. Check HITL approval
    if not state.get("human_approved", False) and not state.get("auto_approve_plan", False):
        return "human_checkpoint"

    pending = state.get("pending_subtasks", [])
    if pending:
        # Sort by priority
        pending_sorted = sorted(pending, key=lambda s: s.priority)
        next_task = pending_sorted[0]
        if next_task.agent == "analyst":
            return "analyst"
        else:
            return "researcher"

    # 2. Check if verification is needed
    critic_reviews = state.get("critic_reviews", [])
    findings = state.get("findings", [])
    if findings and not critic_reviews:
        return "critic"

    # 3. Check if revision loop needed
    critic_objections = state.get("critic_objections", [])
    revision_count = state.get("revision_count", 0)
    if critic_objections and revision_count < 2:
        return "critic_revision"

    # 4. Ready for final synthesis
    return "writer"
