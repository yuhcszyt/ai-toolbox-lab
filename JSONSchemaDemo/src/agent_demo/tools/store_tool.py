from typing import Any

from pydantic import BaseModel, Field

from agent_demo.agent.state import AgentState
from agent_demo.services.store_service import StoreService
from agent_demo.tools.registry import ToolResult


class StoreSearchArguments(BaseModel):
    lat: float = Field(ge=-90, le=90)
    lng: float = Field(ge=-180, le=180)
    category: str = Field(min_length=1)


class StoreSearchTool:
    name = "search_nearby_stores"

    def __init__(self, service: StoreService, max_stores: int) -> None:
        self._service = service
        self._max_stores = max_stores

    def validate_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return StoreSearchArguments.model_validate(arguments).model_dump()

    async def execute(self, arguments: dict[str, Any], state: AgentState) -> ToolResult:
        validated = self.validate_arguments(arguments)
        stores = await self._service.search_nearby(
            validated["lat"], validated["lng"], validated["category"], self._max_stores
        )
        return ToolResult(stores=stores)
