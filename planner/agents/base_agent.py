from abc import ABC, abstractmethod
import traceback
import streamlit as st
from typing import Any
from state.schema import AgentStatus
from utils.logger import logger

class BaseAgent(ABC):
    """Abstract base class for all travel planner agents."""

    name: str = "BaseAgent"

    def set_status(self, status: AgentStatus) -> None:
        """Update this agent's status in session_state."""
        st.session_state.agent_status[self.name] = status

    @abstractmethod
    async def run(self, **kwargs) -> dict:
        """
        Execute the agent's primary task.

        Returns:
            A result dict conforming to this agent's output contract.
        """
        raise NotImplementedError

    def handle_error(self, error: Exception, fallback: dict) -> dict:
        """
        Standard error handler - logs error, returns fallback result.
        Avoids exposing stack traces to the UI (AI mistake e1).
        """
        logger.error(f"[{self.name}] {error}\n{traceback.format_exc()}")
        self.set_status(AgentStatus.ERROR)
        return {**fallback, "status": "error", "error_msg": str(error)}
