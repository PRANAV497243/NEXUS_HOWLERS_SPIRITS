"""
PROJECT NEXUS — Groq API Client with Rate-Limit Handling
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import logging
import time
from typing import List, Optional

from config import GROQ_API_KEY, GROQ_FAST_MODEL, GROQ_STRONG_MODEL

logger = logging.getLogger(__name__)

_groq_client = None

def get_groq_client():
    global _groq_client
    if _groq_client is None and GROQ_API_KEY:
        try:
            from groq import Groq
            _groq_client = Groq(api_key=GROQ_API_KEY)
        except Exception as e:
            logger.warning("Could not initialize Groq client: %s", e)
    return _groq_client

def generate(
    messages: List[dict],
    model: str = GROQ_STRONG_MODEL,
    temperature: float = 0.2,
    max_tokens: int = 3000,
) -> tuple[str, dict]:
    """Call Groq chat completion. Raises Exception on error/rate limit for fallback."""
    client = get_groq_client()
    if client is None:
        raise RuntimeError("Groq client not configured or missing GROQ_API_KEY")

    t0 = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    latency = time.perf_counter() - t0

    content = response.choices[0].message.content or ""
    usage = {
        "provider": "groq",
        "model": model,
        "prompt_tokens": getattr(response.usage, "prompt_tokens", 0) if response.usage else 0,
        "completion_tokens": getattr(response.usage, "completion_tokens", 0) if response.usage else 0,
        "latency_sec": latency,
    }
    return content, usage
