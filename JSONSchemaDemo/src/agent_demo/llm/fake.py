from enum import StrEnum
from typing import Any

from agent_demo.agent.models import FinalAnswerAction, ToolCallAction
from agent_demo.agent.state import AgentState


class FakeScenario(StrEnum):
    PACKAGE_SECOND_STORE = "package_second_store"
    PACKAGE_FIRST_STORE = "package_first_store"
    NO_PACKAGE = "no_package"
    HALLUCINATED_ID = "hallucinated_id"
    ALTERED_DISPLAY_FACTS = "altered_display_facts"
    INVALID_OUTPUT_ONCE = "invalid_output_once"
    INVALID_OUTPUT_TWICE = "invalid_output_twice"
    REPEATED_TOOL_CALL = "repeated_tool_call"
    NEVER_FINAL = "never_final"
    SIXTH_STORE = "sixth_store"
    INVALID_TOOL_NAME = "invalid_tool_name"


class FakeLLM:
    """Deterministic stand-in for an external LLM; it only chooses next actions."""

    def __init__(self, scenario: FakeScenario = FakeScenario.PACKAGE_SECOND_STORE) -> None:
        self.scenario = scenario
        self.final_intent_calls = 0

    async def decide_next_action(self, state: AgentState):
        if self.scenario is FakeScenario.INVALID_TOOL_NAME:
            return ToolCallAction(tool_name="invented_tool", arguments={})
        if self.scenario is FakeScenario.REPEATED_TOOL_CALL:
            return ToolCallAction(
                tool_name="search_nearby_stores",
                arguments={"lat": state.lat, "lng": state.lng, "category": state.category},
            )
        if self.scenario is FakeScenario.NEVER_FINAL:
            return ToolCallAction(
                tool_name="search_nearby_stores",
                arguments={
                    "lat": state.lat + state.loop_count / 1000,
                    "lng": state.lng,
                    "category": state.category,
                },
            )
        if not state.evidence.stores:
            return ToolCallAction(
                tool_name="search_nearby_stores",
                arguments={"lat": state.lat, "lng": state.lng, "category": state.category},
            )

        has_package = any(
            product.is_package
            and product.suitable_people is not None
            and product.suitable_people >= state.people_count
            for product in state.evidence.products.values()
        )
        if has_package:
            return FinalAnswerAction()

        stores = sorted(state.evidence.stores.values(), key=lambda store: store.distance_meters)
        next_store = next(
            (
                store
                for store in stores
                if store.store_id not in state.searched_store_ids
                and store.store_id not in state.timed_out_store_ids
                and store.store_id not in state.failed_store_ids
            ),
            None,
        )
        if next_store is None:
            if self.scenario is FakeScenario.SIXTH_STORE:
                return ToolCallAction(tool_name="search_products", arguments={"store_id": "S6"})
            return FinalAnswerAction()
        return ToolCallAction(
            tool_name="search_products", arguments={"store_id": next_store.store_id}
        )

    async def generate_final_intent(
        self, state: AgentState, feedback: str | None = None
    ) -> dict[str, Any]:
        self.final_intent_calls += 1
        if self.scenario is FakeScenario.INVALID_OUTPUT_TWICE or (
            self.scenario is FakeScenario.INVALID_OUTPUT_ONCE
            and self.final_intent_calls == 1
        ):
            return {"recommendation_type": "NOT_A_VALID_TYPE"}
        products = sorted(
            state.evidence.products.values(),
            key=lambda product: (
                state.evidence.stores[product.store_id].distance_meters,
                product.price,
            ),
        )
        package = next(
            (
                product
                for product in products
                if product.is_package
                and product.suitable_people is not None
                and product.suitable_people >= state.people_count
            ),
            None,
        )
        if package:
            intent = {
                "recommendation_type": "PACKAGE",
                "store_id": package.store_id,
                "product_ids": [package.product_id],
                "reason": "优先选择了已验证的双人套餐。",
            }
        else:
            singles = [product for product in products if not product.is_package]
            intent = {
                "recommendation_type": "SINGLE_ITEMS",
                "store_id": singles[0].store_id,
                "product_ids": [product.product_id for product in singles[:2]],
                "reason": "没有合适套餐，选择了已查询门店的单品。",
            }
        if self.scenario is FakeScenario.HALLUCINATED_ID:
            intent["product_ids"] = ["P9999"]
        if self.scenario is FakeScenario.ALTERED_DISPLAY_FACTS:
            intent["store_name"] = "虚构门店"
            intent["products"] = [
                {"product_id": intent["product_ids"][0], "name": "虚构菜品", "price": 1}
            ]
        return intent
