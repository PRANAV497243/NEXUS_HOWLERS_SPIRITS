"""
PROJECT NEXUS — Code Executor Tool
Sandboxed Python Execution for Data Analysis & Chart Generation
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import base64
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path
from typing import Any

from config import CHARTS_DIR, CODE_EXECUTION_TIMEOUT, SYSTEM_ATTRIBUTION


BLOCKED_PATTERNS = [
    "import os", "import subprocess", "import shutil", "import socket",
    "import urllib", "__import__", "exec(", "eval(", "os.system", "os.popen",
]


class CodeExecutor:
    """Safe Python executor for Data Analyst agent."""

    def __init__(self, output_dir: Path | str | None = None):
        self.output_dir = Path(output_dir) if output_dir else CHARTS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _validate_code(self, code: str) -> tuple[bool, str]:
        for pattern in BLOCKED_PATTERNS:
            if pattern in code:
                return False, f"Restricted operation detected: '{pattern}'"
        return True, "OK"

    def _wrap_code(self, code: str, chart_path: str) -> str:
        escaped_chart_path = chart_path.replace("\\", "/")
        return f"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import json

plt.style.use('default')
plt.rcParams['figure.figsize'] = (9, 5)
plt.rcParams['font.size'] = 10
fig, ax = plt.subplots()

# --- User Script ---
{code}

# --- Automatic Chart Styling & Saving ---
plt.figtext(0.99, 0.01, "{SYSTEM_ATTRIBUTION}", horizontalalignment='right', fontsize=8, color='gray', style='italic')
plt.tight_layout()
plt.savefig(r"{escaped_chart_path}", dpi=150)
plt.close('all')
print("[NEXUS_CHART_SAVED]")
"""

    def execute(self, code: str) -> dict[str, Any]:
        """Execute Python code and return execution logs and generated chart path."""
        valid, reason = self._validate_code(code)
        if not valid:
            return {"success": False, "stdout": "", "stderr": reason, "chart_path": None}

        chart_filename = f"chart_{uuid.uuid4().hex[:8]}.png"
        chart_path = self.output_dir / chart_filename

        wrapped_code = self._wrap_code(code, str(chart_path))

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as tmp:
            tmp.write(wrapped_code)
            tmp_path = tmp.name

        try:
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=CODE_EXECUTION_TIMEOUT,
            )
            chart_exists = chart_path.exists() and chart_path.stat().st_size > 0
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "chart_path": str(chart_path) if chart_exists else None,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out ({CODE_EXECUTION_TIMEOUT}s)",
                "chart_path": None,
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "chart_path": None,
            }
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
