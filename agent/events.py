from __future__ import annotations
from enum import Enum
from dataclasses import dataclass, field
from typing import Any

from client.response import TokenUsage

class AgentEventType(str, Enum):
    # Agent Lifecycle Events
    AGENT_START = "agent_start"
    AGENT_END = "agent_end"
    AGENT_ERROR = "agent_error"

    # Text Streaming Events
    TEXT_DELTA = "text_delta"
    TEXT_COMPLETE = "text_complete"

@dataclass
class AgentEvent:
    type: AgentEventType
    data: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def agent_start(cls, message: str) -> AgentEvent:
        return cls(type=AgentEventType.AGENT_START, data={"message": message})

    @classmethod
    def agent_end(cls, response: str | None, usage: TokenUsage | None) -> AgentEvent:
        return cls(type=AgentEventType.AGENT_END, data={"response": response, "usage": usage.__dict__ if usage else None})

    @classmethod
    def agent_error(cls, message: str) -> AgentEvent:
        return cls(type=AgentEventType.AGENT_ERROR, data={"message": message})