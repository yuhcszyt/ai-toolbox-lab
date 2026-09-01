from typing import Any

from pydantic import BaseModel, Field

from agent_demo.agent.state import AgentState
from agent_demo.services.product_service import ProductService
from agent_demo.tools.registry import ToolResult


class ProductSearchArguments(BaseModel):
    store_id: str = Field(min_length=1)


class ProductSearchTool:
    name = "search_products"

    def __init__(self, service: ProductService) -> None:
        self._service = service

    def validate_arguments(self, arguments: dict[str, Any]) -> dict[str, Any]:
        return ProductSearchArguments.model_validate(arguments).model_dump()

    async def execute(self, arguments: dict[str, Any], state: AgentState) -> ToolResult:
        store_id = self.validate_arguments(arguments)["store_id"]
        if store_id not in state.evidence.stores:
            raise ValueError("search_products requires a store ID returned by search_nearby_stores")
        products = await self._service.search_products(store_id)
        return ToolResult(products=products)
