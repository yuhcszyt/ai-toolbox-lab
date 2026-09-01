import logging
import time
from dataclasses import dataclass, field
from typing import Any

from agent_demo.agent.state import AgentState


logger = logging.getLogger("agent_demo")


@dataclass(frozen=True)
class TraceEvent:
    name: str
    request_id: str
    session_id: str
    trace_id: str
    timestamp: float
    data: dict[str, Any] = field(default_factory=dict)


class TraceRecorder:
    """Keeps concise operational events; it never receives hidden LLM reasoning."""

    def __init__(self) -> None:
        self.events: list[TraceEvent] = []

    def emit(self, state: AgentState, name: str, **data: Any) -> None:
        event = TraceEvent(
            name=name,
            request_id=state.request_id,
            session_id=state.session_id,
            trace_id=state.request_id,
            timestamp=time.time(),
            data=data,
        )
        self.events.append(event)
        logger.info("agent_event=%s request_id=%s data=%s", name, state.request_id, data)

