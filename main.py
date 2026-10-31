"""
PROJECT NEXUS — Main FastAPI Application
Autonomous Multi-Agent AI Problem Solver Backend & Web Server
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import PROJECT_NAME, REPORTS_DIR, SYSTEM_ATTRIBUTION
from orchestrator import run_research

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("nexus.main")

app = FastAPI(
    title=PROJECT_NAME,
    description=f"Autonomous Multi-Agent AI Problem Solver API. {SYSTEM_ATTRIBUTION}",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"


class TaskRequest(BaseModel):
    query: str
    auto_approve: bool = True
    session_id: Optional[str] = None


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "system": PROJECT_NAME,
        "attribution": SYSTEM_ATTRIBUTION,
    }


@app.post("/api/run")
def run_task(req: TaskRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    logger.info(f"Received problem solving request: {req.query[:60]}")
    try:
        result = run_research(query=req.query, auto_approve=req.auto_approve)
        return {
            "status": "success",
            "query": result.get("query"),
            "research_plan": result.get("research_plan"),
            "findings_count": len(result.get("findings", [])),
            "insights_count": len(result.get("data_insights", [])),
            "critic_reviews": result.get("critic_reviews", []),
            "final_report": result.get("final_report"),
            "agent_messages": result.get("agent_messages", []),
            "docx_path": result.get("docx_path"),
            "attribution": SYSTEM_ATTRIBUTION,
        }
    except Exception as e:
        logger.error(f"Error during agent orchestration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/download/{filename}")
def download_docx(filename: str):
    file_path = REPORTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Requested report file not found.")
    return FileResponse(
        path=file_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=filename,
    )


# Serve frontend static files
if FRONTEND_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

    @app.get("/", response_class=HTMLResponse)
    def index():
        index_file = FRONTEND_DIR / "index_1.html"
        if index_file.exists():
            return HTMLResponse(content=index_file.read_text(encoding="utf-8"))
        return HTMLResponse(content=f"<h1>{PROJECT_NAME}</h1><p>{SYSTEM_ATTRIBUTION}</p>")

    @app.get("/style.css")
    def style_css():
        css_file = FRONTEND_DIR / "style.css"
        return FileResponse(css_file, media_type="text/css")

    @app.get("/script.js")
    def script_js():
        js_file = FRONTEND_DIR / "script.js"
        return FileResponse(js_file, media_type="application/javascript")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
