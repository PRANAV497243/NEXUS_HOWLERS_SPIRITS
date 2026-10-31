"""
PROJECT NEXUS — Interactive Test & Demo Runner
Run this script to test the complete multi-agent workflow end-to-end.
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import sys
import os

# Ensure safe UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from orchestrator import run_research_stream
from config import SYSTEM_ATTRIBUTION, PROJECT_NAME

def run_nexus_test(query: str):
    print("=" * 75)
    print(f"  [+] {PROJECT_NAME} -- LIVE MULTI-AGENT EXECUTION TEST")
    print(f"  {SYSTEM_ATTRIBUTION}")
    print("=" * 75)
    print(f"\n[USER OBJECTIVE]:\n  \"{query}\"\n")
    print("-" * 75)
    print("  AGENT COLLABORATION STREAM:")
    print("-" * 75)

    final_state = None
    seen_messages = 0

    # Stream the multi-agent graph execution
    for state in run_research_stream(query, auto_approve=True):
        final_state = state
        messages = state.get("agent_messages", [])
        
        # Print newly arrived agent activity messages
        while seen_messages < len(messages):
            msg = messages[seen_messages]
            agent_badge = f"[{msg.agent.upper():^14}]"
            print(f"{agent_badge} {msg.message}")
            seen_messages += 1

    print("\n" + "=" * 75)
    print("  WORKFLOW EXECUTION SUMMARY")
    print("=" * 75)

    if final_state and final_state.get("final_report"):
        report = final_state["final_report"]
        print(f"✅ Status: COMPLETED")
        print(f"📌 Report Title: {report.title}")
        print(f"🔍 Findings Gathered: {len(final_state.get('findings', []))}")
        print(f"📊 Quantitative Insights: {len(final_state.get('data_insights', []))}")
        
        critic_reviews = final_state.get("critic_reviews", [])
        if critic_reviews:
            last_review = critic_reviews[-1]
            print(f"🛡️ Critic Verification Score: {last_review.score}/100 (Approved: {last_review.is_approved})")

        docx_path = final_state.get("docx_path")
        if docx_path and os.path.exists(docx_path):
            print(f"📄 Word Report (.docx): {docx_path}")

        print("\n" + "-" * 75)
        print("  EXECUTIVE SUMMARY:")
        print("-" * 75)
        print(report.executive_summary)
        
        print("\n" + "-" * 75)
        print("  FIRST 300 CHARACTERS OF FINAL SYNTHESIS:")
        print("-" * 75)
        print(report.markdown[:300] + "...\n")
    else:
        print("❌ Workflow finished with errors or no report generated.")

    print("=" * 75)
    print(f"  {SYSTEM_ATTRIBUTION}")
    print("=" * 75)

if __name__ == "__main__":
    test_query = (
        "Analyze the adoption of Autonomous Multi-Agent AI systems in healthcare, "
        "including clinical diagnostic accuracy, workflow speedups, and compliance challenges."
    )
    if len(sys.argv) > 1:
        test_query = " ".join(sys.argv[1:])
    
    run_nexus_test(test_query)
