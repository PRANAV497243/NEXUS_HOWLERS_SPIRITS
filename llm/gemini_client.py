"""
PROJECT NEXUS — Google Gemini API Client with Rate-Limit Handling
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import logging
import time
from typing import List

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_STRONG_MODEL

logger = logging.getLogger(__name__)

_gemini_client = None

def get_gemini_client():
    global _gemini_client
    if _gemini_client is None and GEMINI_API_KEY:
        try:
            # Check for new google-genai or google-generativeai
            import google.generativeai as genai
            genai.configure(api_key=GEMINI_API_KEY)
            _gemini_client = genai
        except Exception as e:
            logger.warning("Could not initialize Gemini client: %s", e)
    return _gemini_client

def generate(
    messages: List[dict],
    model: str = GEMINI_STRONG_MODEL,
    temperature: float = 0.2,
    max_tokens: int = 3000,
) -> tuple[str, dict]:
    """Call Gemini chat completion. Raises Exception on error/rate limit (429) for fallback."""
    client = get_gemini_client()
    if client is None:
        raise RuntimeError("Gemini client not configured or missing GEMINI_API_KEY")

    t0 = time.perf_counter()
    
    # Map messages to Gemini prompt format
    system_instruction = None
    formatted_contents = []
    
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        if role == "system":
            system_instruction = content
        elif role in ("assistant", "model"):
            formatted_contents.append({"role": "model", "parts": [content]})
        else:
            formatted_contents.append({"role": "user", "parts": [content]})

    # Fallback to simple prompt if only user messages
    gen_model = client.GenerativeModel(
        model_name=model,
        system_instruction=system_instruction
    )
    
    # Simple generation from latest turn or history
    if len(formatted_contents) == 1:
        response = gen_model.generate_content(
            formatted_contents[0]["parts"][0],
            generation_config=client.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )
    else:
        chat = gen_model.start_chat(history=formatted_contents[:-1])
        last_turn = formatted_contents[-1]["parts"][0]
        response = chat.send_message(
            last_turn,
            generation_config=client.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
        )

    latency = time.perf_counter() - t0
    content = response.text if hasattr(response, "text") else ""
    
    usage = {
        "provider": "gemini",
        "model": model,
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "latency_sec": latency,
    }
    return content, usage
