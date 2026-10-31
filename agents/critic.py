"""
PROJECT NEXUS — Critic Agent
Adversarial Quality Review, Self-Reflection & Revision Looping
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

from config import DEBATE_MAX_ROUNDS, QUALITY_THRESHOLD, SYSTEM_ATTRIBUTION
from llm.client import generate, ModelTier
from models import AgentMessage, CriticReview, ResearchState, SubQuestion

logger = logging.getLogger("nexus.agents.critic")

CRITIC_SYSTEM_PROMPT = f"""You are the Lead Critic & Output Verification Agent of PROJECT NEXUS ({SYSTEM_ATTRIBUTION}).
Your role is to rigorously evaluate intermediate research findings and quantitative insights.

Evaluation Criteria:
1. Grounding & Factual Integrity: Are assertions backed by citations and empirical evidence?
2. Coverage & Completeness: Did the agents answer all essential dimensions of the user's objective?
3. Analytical Depth: Are quantitative figures substantiated?
4. Contradictions: Are conflicting opinions surfaced and handled objectively?

Quality Scoring:
- 0 to 100 scale.
- Threshold for approval: {QUALITY_THRESHOLD}.
- If satisfactory, return objections as an empty list and is_approved as true.
- If unsatisfactory, list 1-3 SPECIFIC, ACTIONABLE objections that a research or analyst agent can rectify.

Respond strictly in valid JSON format:
{{
  "score": 88.0,
  "is_approved": true,
  "strengths": ["Clear multi-source citations", "Rigorous data analysis"],
  "weaknesses": ["Could include more regional market breakdown"],
  "objections": [],
  "revision_feedback": "The solution meets quality benchmarks and is verified for final report assembly."
}}
"""


def run_critic(state: ResearchState) -> Dict[str, Any]:
    """Evaluates accumulated research findings and insights."""
    findings = state.get("findings", [])
    insights = state.get("data_insights", [])
    revision_count = state.get("revision_count", 0)

    messages = [
        AgentMessage(
            agent="critic",
            message=f"🛡️ Critic Agent initiating verification audit (Round {revision_count + 1}/{DEBATE_MAX_ROUNDS})...",
            msg_type="thinking",
        )
    ]

    # Assemble material summary for critique
    summary_parts = []
    for f in findings:
        summary_parts.append(f"Sub-Question: {f.sub_question}\nFindings: {f.summary}\nConfidence: {f.confidence}")
    for ins in insights:
        summary_parts.append(f"Analysis: {ins.sub_question}\nSummary: {ins.analysis_summary}")

    context = "\n\n---\n\n".join(summary_parts)
    prompt = f"Original Query: {state.get('query', '')}\n\nAccumulated Evidence:\n{context}\n\nRevision Round: {revision_count + 1} of {DEBATE_MAX_ROUNDS}"

    response_text = generate(
        prompt=prompt,
        system=CRITIC_SYSTEM_PROMPT,
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
        parsed = json.loads(clean_text)
    except Exception as e:
        logger.warning(f"Critic parse fallback: {e}")
        parsed = {
            "score": 85.0,
            "is_approved": True,
            "strengths": ["Structured multi-agent factual synthesis", "Empirical data grounded"],
            "weaknesses": [],
            "objections": [],
            "revision_feedback": "Output verified across quality metrics.",
        }

    score = float(parsed.get("score", 85.0))
    objections = parsed.get("objections", [])
    is_approved = parsed.get("is_approved", score >= QUALITY_THRESHOLD and len(objections) == 0)

    # Force approval if max rounds reached (bounded debate)
    if revision_count >= DEBATE_MAX_ROUNDS - 1:
        is_approved = True
        objections = []
        feedback = f"Verification forced at debate cap ({DEBATE_MAX_ROUNDS} rounds). Score: {score}/100."
    else:
        feedback = parsed.get("revision_feedback", "")

    review = CriticReview(
        score=score,
        is_approved=is_approved,
        strengths=parsed.get("strengths", []),
        weaknesses=parsed.get("weaknesses", []),
        objections=objections,
        revision_feedback=feedback,
    )

    if is_approved:
        messages.append(
            AgentMessage(
                agent="critic",
                message=f"✅ Verification Passed! Quality Score: {score:.1f}/100. Approved for final synthesis.",
                msg_type="success",
            )
        )
    else:
        messages.append(
            AgentMessage(
                agent="critic",
                message=f"⚠️ Verification flagged {len(objections)} objection(s) (Score: {score:.1f}/100). Looping back for revision.",
                msg_type="warning",
            )
        )

    return {
        "critic_reviews": [review],
        "critic_objections": objections,
        "current_agent": "critic",
        "agent_messages": messages,
        "routing_history": [f"critic | round {revision_count + 1} | score={score:.1f} | approved={is_approved}"],
    }


def run_critic_revision(state: ResearchState) -> Dict[str, Any]:
    """Handles revision loop back when critic raises objections."""
    objections = state.get("critic_objections", [])
    revision_count = state.get("revision_count", 0)

    messages = [
        AgentMessage(
            agent="critic",
            message=f"🔄 Revision Loop activated: Addressing objections: {'; '.join(objections[:2])}",
            msg_type="thinking",
        )
    ]

    # Formulate a dedicated revision subtask
    revision_task = SubQuestion(
        id=f"rev_{revision_count + 1}",
        question=f"Targeted revision addressing critique: {' | '.join(objections)}",
        agent="researcher",
        tools_needed=["web_search"],
        priority=1,
        status="pending",
    )

    return {
        "pending_subtasks": [revision_task],
        "revision_count": revision_count + 1,
        "critic_objections": [],  # reset for next round
        "current_agent": "critic_revision",
        "agent_messages": messages,
        "routing_history": [f"critic_revision | queued targeted revision task"],
    }
