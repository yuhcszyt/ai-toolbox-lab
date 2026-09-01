from typing import Any, Protocol

from agent_demo.agent.models import AgentAction
from agent_demo.agent.state import AgentState


class LLMClient(Protocol):
    async def decide_next_action(self, state: AgentState) -> AgentAction: ...

    async def generate_final_intent(self, state: AgentState, feedback: str | None = None) -> Any: ...

