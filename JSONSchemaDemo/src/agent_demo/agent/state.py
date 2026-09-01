from typing import Any

from pydantic import BaseModel, Field

from agent_demo.dto.domain import Product, RecommendationIntent, Store


class EvidenceStore(BaseModel):
    """Facts returned by tools during one run only."""

    stores: dict[str, Store] = Field(default_factory=dict)
    products: dict[str, Product] = Field(default_factory=dict)

    def record_stores(self, stores: list[Store]) -> None:
        self.stores.update({store.store_id: store for store in stores})

    def record_products(self, products: list[Product]) -> None:
        self.products.update({product.product_id: product for product in products})


class AgentState(BaseModel):
    request_id: str
    session_id: str
    user_query: str
    lat: float
    lng: float
    category: str = "川菜"
    people_count: int = 2

    messages: list[dict[str, Any]] = Field(default_factory=list)
    tool_calls: list[dict[str, Any]] = Field(default_factory=list)
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    tool_call_count: int = 0
    loop_count: int = 0

    considered_store_ids: list[str] = Field(default_factory=list)
    searched_store_ids: list[str] = Field(default_factory=list)
    failed_store_ids: list[str] = Field(default_factory=list)
    timed_out_store_ids: list[str] = Field(default_factory=list)

    selected_store_id: str | None = None
    selected_product_ids: list[str] = Field(default_factory=list)

    stores: dict[str, Store] = Field(default_factory=dict)
    products: dict[str, Product] = Field(default_factory=dict)
    evidence: EvidenceStore = Field(default_factory=EvidenceStore)
    final_intent: RecommendationIntent | None = None
    executed_tool_signatures: dict[str, int] = Field(default_factory=dict)
