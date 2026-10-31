"""
PROJECT NEXUS — Workflow Engine
High-Level Multi-Agent Execution & Asynchronous Task Orchestration
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import asyncio
import logging
from typing import Any, AsyncGenerator, Dict, Optional

from orchestrator import run_research, run_research_stream
from models import ResearchState

logger = logging.getLogger("nexus.workflow")


class NexusWorkflow:
    """High-level async interface to run Project Nexus problem-solving workflows."""

    def __init__(self, auto_approve: bool = True):
        self.auto_approve = auto_approve

    async def execute_task(self, query: str) -> ResearchState:
        """Asynchronously runs complete multi-agent workflow."""
        return await asyncio.to_thread(run_research, query, self.auto_approve)

    async def stream_task(self, query: str) -> AsyncGenerator[Dict[str, Any], None]:
        """Asynchronously streams step events as agents collaborate."""
        def _get_stream():
            return list(run_research_stream(query, self.auto_approve))
        
        events = await asyncio.to_thread(_get_stream)
        for evt in events:
            yield evt
            await asyncio.sleep(0.05)


def run_pipeline(query: str, auto_approve: bool = True) -> Dict[str, Any]:
    """Convenience synchronous function."""
    return run_research(query, auto_approve=auto_approve)
