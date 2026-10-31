"""
PROJECT NEXUS — Autonomous Multi-Agent AI Problem Solver
Configuration & System Settings
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Base Directory Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CHARTS_DIR = DATA_DIR / "charts"
REPORTS_DIR = DATA_DIR / "reports"
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", str(DATA_DIR / "chroma_db"))

CHARTS_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR.mkdir(parents=True, exist_ok=True)

# --- API Keys ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")

# --- Multi-LLM Routing & Resilience ---
# Primary -> Secondary -> Fallback rotation
GROQ_FAST_MODEL = os.getenv("GROQ_FAST_MODEL", "llama-3.1-8b-instant")
GROQ_STRONG_MODEL = os.getenv("GROQ_STRONG_MODEL", "llama-3.3-70b-versatile")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_STRONG_MODEL = os.getenv("GEMINI_STRONG_MODEL", "gemini-1.5-pro")
OPENAI_FALLBACK_MODEL = os.getenv("OPENAI_FALLBACK_MODEL", "gpt-4o-mini")

# Agent Specific Preferred Models
PLANNER_MODEL = os.getenv("PLANNER_MODEL", "llama-3.3-70b-versatile")
RESEARCHER_MODEL = os.getenv("RESEARCHER_MODEL", "llama-3.1-8b-instant")
ANALYST_MODEL = os.getenv("ANALYST_MODEL", "llama-3.3-70b-versatile")
CRITIC_MODEL = os.getenv("CRITIC_MODEL", "llama-3.3-70b-versatile")
WRITER_MODEL = os.getenv("WRITER_MODEL", "llama-3.3-70b-versatile")

# Rate Limiting & Backoff Configuration
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))
LLM_BACKOFF_BASE = float(os.getenv("LLM_BACKOFF_BASE", "2.0"))
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.2"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "4096"))

# --- Execution & Verification Limits ---
MAX_SUB_QUESTIONS = int(os.getenv("MAX_SUB_QUESTIONS", "5"))
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "5"))
REPORT_MAX_WORDS = int(os.getenv("REPORT_MAX_WORDS", "3000"))
CODE_EXECUTION_TIMEOUT = int(os.getenv("CODE_EXECUTION_TIMEOUT", "30"))
DEBATE_MAX_ROUNDS = int(os.getenv("DEBATE_MAX_ROUNDS", "2"))
QUALITY_THRESHOLD = float(os.getenv("QUALITY_THRESHOLD", "75.0"))  # Score out of 100

# --- Human In The Loop ---
AUTO_APPROVE_PLAN = os.getenv("AUTO_APPROVE_PLAN", "False").lower() in ("true", "1", "yes")

# --- Attribution ---
SYSTEM_ATTRIBUTION = "Developed by Pranav, AI & DE Branch"
PROJECT_NAME = "PROJECT NEXUS"
