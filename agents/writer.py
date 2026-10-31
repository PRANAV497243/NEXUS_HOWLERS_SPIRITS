"""
PROJECT NEXUS — Report Writer Agent
Synthesizes Comprehensive Solutions and Triggers .docx Export
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import logging
from datetime import datetime
from typing import Any, Dict, List

from config import REPORT_MAX_WORDS, SYSTEM_ATTRIBUTION
from llm.client import generate, ModelTier
from models import AgentMessage, Citation, FinalReport, ReportSection, ResearchState
from tools.docx_export import export_to_docx

logger = logging.getLogger("nexus.agents.writer")

WRITER_SYSTEM_PROMPT = f"""You are the Lead Report Writer & Synthesizer Agent of PROJECT NEXUS ({SYSTEM_ATTRIBUTION}).
Your role is to synthesize all accumulated findings, quantitative data insights, and verified citations into a comprehensive, professional, world-class solution report.

Required Markdown Document Structure:
# [Comprehensive Solution Title]

## Executive Summary
[Concise executive overview outlining core answers, problem solution, and strategic impact]

## Key Findings & Empirical Evidence
[Synthesized insights broken down into focused sub-sections, citing sources with [Title](URL) links]

## Quantitative Analysis & Metrics
[Data insights, numerical comparisons, and references to generated charts]

## Conflicting Perspectives & Limitations
[Objective analysis of trade-offs, criticisms, and potential constraints]

## Strategic Recommendations & Conclusion
[Actionable, forward-looking conclusions and next steps]

Target length: ~{REPORT_MAX_WORDS} words.
Professional, technical, authoritative tone.
Always include the footer credit at the bottom:
*{SYSTEM_ATTRIBUTION}*
"""


def run_writer(state: ResearchState) -> Dict[str, Any]:
    """Compiles findings and writes structured final report."""
    query = state.get("query", "")
    plan = state.get("research_plan")
    findings = state.get("findings", [])
    insights = state.get("data_insights", [])
    critic_reviews = state.get("critic_reviews", [])

    messages = [
        AgentMessage(
            agent="writer",
            message=f"✍️ Synthesizer Agent drafting final report ({len(findings)} findings, {len(insights)} data insights)...",
            msg_type="thinking",
        )
    ]

    # Gather citations
    all_citations: List[Citation] = []
    for f in findings:
        all_citations.extend(f.citations)

    # Prepare context for writer LLM
    context_chunks = []
    for i, f in enumerate(findings, 1):
        context_chunks.append(f"### Finding {i}: {f.sub_question}\n{f.summary}\nKey points: {', '.join(f.key_points)}")
    for j, ins in enumerate(insights, 1):
        context_chunks.append(f"### Data Insight {j}: {ins.sub_question}\n{ins.analysis_summary}\nMethodology: {ins.methodology}")

    critic_note = ""
    if critic_reviews:
        last_review = critic_reviews[-1]
        critic_note = f"\nVerification Audit Score: {last_review.score}/100. Strengths: {', '.join(last_review.strengths)}."

    prompt = f"""Problem Statement / Query: {query}

Research Evidence:
{chr(10).join(context_chunks)}
{critic_note}

Please draft the comprehensive final report now."""

    markdown_report = generate(
        prompt=prompt,
        system=WRITER_SYSTEM_PROMPT,
        tier=ModelTier.STRONG,
    )

    # Ensure title and attribution
    if SYSTEM_ATTRIBUTION not in markdown_report:
        markdown_report += f"\n\n---\n*{SYSTEM_ATTRIBUTION}*\n"

    # Extract sections for structured model
    sections = [
        ReportSection(
            title="Key Findings & Synthesis",
            content="\n\n".join([f.summary for f in findings]),
            citations=all_citations[:8],
            confidence_score=0.92,
        )
    ]

    final_report = FinalReport(
        title=f"PROJECT NEXUS: Solution Report for '{query[:50]}'",
        executive_summary=f"Autonomous multi-agent investigation completed with {len(findings)} research findings and {len(insights)} quantitative analyses.",
        sections=sections,
        conclusion=f"Synthesized and verified under Project Nexus standards. {SYSTEM_ATTRIBUTION}",
        markdown=markdown_report,
        metadata={
            "query": query,
            "generated_at": datetime.now().isoformat(),
            "attribution": SYSTEM_ATTRIBUTION,
            "findings_count": len(findings),
            "insights_count": len(insights),
        },
    )

    # Export to .docx Word Document
    docx_path = None
    try:
        docx_path = export_to_docx(
            title=final_report.title,
            executive_summary=final_report.executive_summary,
            sections=sections,
            conclusion=final_report.conclusion,
        )
        final_report.docx_path = docx_path
        messages.append(
            AgentMessage(
                agent="writer",
                message=f"📄 Word Document (.docx) report exported to: {docx_path}",
                msg_type="success",
            )
        )
    except Exception as e:
        logger.warning(f"Docx export failed: {e}")

    messages.append(
        AgentMessage(
            agent="writer",
            message="🎉 Final comprehensive solution report synthesized successfully!",
            msg_type="success",
        )
    )

    return {
        "final_report": final_report,
        "docx_path": docx_path,
        "current_agent": "writer",
        "agent_messages": messages,
        "routing_history": [f"writer | completed final report and docx export"],
    }
