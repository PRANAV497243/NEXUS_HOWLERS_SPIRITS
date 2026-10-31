"""
PROJECT NEXUS — Base Agent Architecture
Developed by Pranav, AI & DE Branch
"""
from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict

from models import AgentMessage

logger = logging.getLogger("nexus.agents")


class BaseAgent(ABC):
    """Abstract base class for all specialized Project Nexus agents."""

    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role

    def log_message(self, message: str, msg_type: str = "info") -> AgentMessage:
        return AgentMessage(agent=self.name, message=message, msg_type=msg_type)

    @abstractmethod
    def run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent responsibility on state."""
        pass
