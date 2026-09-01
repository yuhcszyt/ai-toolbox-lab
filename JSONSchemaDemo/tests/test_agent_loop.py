import asyncio

from agent_demo.agent.models import ToolCallAction
from agent_demo.app import AgentDemoApp, create_demo_app
from agent_demo.agent.policy import AgentPolicy
from agent_demo.llm.fake import FakeScenario
from agent_demo.repositories.mock_repository import MockRestaurantRepository


def test_package_at_second_store_uses_trusted_evidence_and_stops_early():
    app = create_demo_app(FakeScenario.PACKAGE_SECOND_STORE)

    run = asyncio.run(
        app.run(
            user_query="帮我找附近评分高的川菜，两个人吃，最好有套餐。",
            lat=31.2304,
            lng=121.4737,
        )
    )

    assert run.response.status == "SUCCESS"
    assert run.response.recommendation_type == "PACKAGE"
    assert run.response.store_id == "S2"
    assert [product.product_id for product in run.response.products] == ["P2001"]
    assert "P2001" in run.state.evidence.products
    assert app.repository.product_call_counts["S1"] == 1
    assert app.repository.product_call_counts["S2"] == 1
    assert app.repository.product_call_counts["S3"] == 0


def test_package_at_first_store_stops_before_second_store_is_queried():
    app = create_demo_app(FakeScenario.PACKAGE_FIRST_STORE)

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "SUCCESS"
    assert run.response.store_id == "S1"
    assert app.repository.product_call_counts["S1"] == 1
    assert app.repository.product_call_counts["S2"] == 0


def test_no_package_falls_back_to_singles_from_all_five_tool_results():
    app = create_demo_app(FakeScenario.NO_PACKAGE)

    run = asyncio.run(
        app.run(
            user_query="帮我找附近评分高的川菜，两个人吃，没有套餐就推荐单品。",
            lat=31.2304,
            lng=121.4737,
        )
    )

    assert run.response.status == "SUCCESS"
    assert run.response.recommendation_type == "SINGLE_ITEMS"
    assert len(run.state.searched_store_ids) == 5
    assert all(app.repository.product_call_counts[store_id] == 1 for store_id in run.state.searched_store_ids)
    assert all(
        product.product_id in run.state.evidence.products for product in run.response.products
    )


def test_repeated_identical_tool_call_is_blocked_by_runtime_policy():
    app = create_demo_app(
        FakeScenario.REPEATED_TOOL_CALL,
        policy=AgentPolicy(max_same_tool_call_repeats=0),
    )

    run = asyncio.run(
        app.run("找附近川菜。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "FAILED"
    assert run.state.tool_call_count == 1
    assert run.state.loop_count == 2
    assert any("repeated tool call" in warning for warning in run.response.warnings)


def test_loop_budget_returns_controlled_failure_when_llm_never_finishes():
    app = create_demo_app(
        FakeScenario.NEVER_FINAL,
        policy=AgentPolicy(max_loop_count=3, max_tool_calls=10),
    )

    run = asyncio.run(
        app.run("持续找附近川菜。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "FAILED"
    assert run.state.loop_count == 3
    assert run.state.tool_call_count == 3
    assert run.response.warnings == ["loop budget exhausted"]


def test_invalid_tool_arguments_are_rejected_before_any_tool_execution():
    class InvalidArgumentsLLM:
        async def decide_next_action(self, state):
            return ToolCallAction(
                tool_name="search_nearby_stores",
                arguments={"lat": "not-a-number", "lng": state.lng, "category": state.category},
            )

        async def generate_final_intent(self, state, feedback=None):
            raise AssertionError("invalid action must not reach final output generation")

    app = AgentDemoApp(MockRestaurantRepository.package_second_store(), InvalidArgumentsLLM())

    run = asyncio.run(
        app.run("找附近川菜。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "FAILED"
    assert run.state.tool_call_count == 0
    assert "invalid arguments" in run.response.warnings[0]


def test_sixth_store_request_is_rejected_after_five_stores_are_considered():
    repository = MockRestaurantRepository.no_package()
    app = create_demo_app(
        FakeScenario.SIXTH_STORE,
        repository=repository,
        policy=AgentPolicy(max_stores=5),
    )

    run = asyncio.run(
        app.run("找川菜，没有套餐就继续找。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "FAILED"
    assert len(run.state.searched_store_ids) == 5
    assert repository.product_call_counts["S6"] == 0


def test_unknown_tool_name_returns_controlled_failure_without_execution():
    app = create_demo_app(FakeScenario.INVALID_TOOL_NAME)

    run = asyncio.run(
        app.run("找附近川菜。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "FAILED"
    assert run.state.tool_call_count == 0
    assert run.response.warnings == ["unknown tool: invented_tool"]

