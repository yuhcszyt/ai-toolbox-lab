from dataclasses import dataclass, field
from typing import Any, Protocol

from agent_demo.agent.state import AgentState
from agent_demo.dto.domain import Product, Store


@dataclass
class ToolResult:
    stores: list[Store] = field(default_factory=list)
    products: list[Product] = field(default_factory=list)


class AgentTool(Protocol):
    """Local tools and future MCP adapters share this boundary with the runtime."""

    name: str

    def validate_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]: ...

    async def execute(self, arguments: dict[str, Any], state: AgentState) -> ToolResult: ...


class ToolRegistry:
    def __init__(self, tools: list[AgentTool]) -> None:
        self._tools = {tool.name: tool for tool in tools}

    def get(self, name: str) -> AgentTool | None:
        return self._tools.get(name)
