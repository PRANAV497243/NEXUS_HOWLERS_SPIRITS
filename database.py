"""
PROJECT NEXUS — Database & Persistence Layer
ChromaDB Vector Store & Session History
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from memory.vector_store import ResearchMemory

logger = logging.getLogger("nexus.database")

_memory_instance: Optional[ResearchMemory] = None

def get_database() -> ResearchMemory:
    """Singleton getter for Project Nexus vector database."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = ResearchMemory()
    return _memory_instance

def save_session_report(query: str, findings: List[Any], report_markdown: str, metadata: Dict[str, Any] | None = None) -> str:
    """Persists a completed session to ChromaDB memory."""
    db = get_database()
    findings_dicts = []
    for f in findings:
        if hasattr(f, "model_dump"):
            findings_dicts.append(f.model_dump())
        elif isinstance(f, dict):
            findings_dicts.append(f)
        else:
            findings_dicts.append({"summary": str(f)})
    return db.store_research(query=query, findings=findings_dicts, report_markdown=report_markdown, metadata=metadata)

def search_related_history(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Searches past problem-solving sessions for semantic matches."""
    db = get_database()
    return db.recall_similar_research(query=query, n_results=limit)
