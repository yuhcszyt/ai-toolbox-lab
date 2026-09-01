import asyncio

from agent_demo.agent.policy import AgentPolicy
from agent_demo.agent.runtime import AgentRuntime
from agent_demo.app import create_demo_app
from agent_demo.llm.fake import FakeScenario
from agent_demo.repositories.mock_repository import MockRestaurantRepository
from agent_demo.tools.registry import ToolRegistry


def test_timeout_is_retried_once_and_second_attempt_can_succeed():
    repository = MockRestaurantRepository.package_second_store()
    repository.set_product_delays("S1", [0.03, 0.0])
    app = create_demo_app(
        FakeScenario.PACKAGE_SECOND_STORE,
        repository=repository,
        policy=AgentPolicy(tool_timeout_seconds=0.01, retry_count=1),
    )

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "SUCCESS"
    assert repository.product_call_counts["S1"] == 2
    assert run.state.timed_out_store_ids == []
    assert any(message["type"] == "tool_retry" for message in run.state.messages)


def test_store_that_times_out_twice_is_skipped_and_agent_can_continue():
    repository = MockRestaurantRepository.package_second_store()
    repository.set_product_delays("S1", [0.03, 0.03])
    app = create_demo_app(
        FakeScenario.PACKAGE_SECOND_STORE,
        repository=repository,
        policy=AgentPolicy(tool_timeout_seconds=0.01, retry_count=1),
    )

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "SUCCESS"
    assert run.response.store_id == "S2"
    assert repository.product_call_counts["S1"] == 2
    assert repository.product_call_counts["S2"] == 1
    assert run.state.timed_out_store_ids == ["S1"]


def test_total_request_deadline_returns_controlled_failure():
    repository = MockRestaurantRepository.package_second_store()
    repository.set_product_delays("S1", [0.05])
    app = create_demo_app(
        FakeScenario.PACKAGE_SECOND_STORE,
        repository=repository,
        policy=AgentPolicy(
            tool_timeout_seconds=1.0,
            retry_count=0,
            total_deadline_seconds=0.01,
        ),
    )

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "FAILED"
    assert run.response.warnings == ["total request deadline exceeded"]


def test_bounded_execution_never_exceeds_policy_concurrency():
    runtime = AgentRuntime(ToolRegistry([]), AgentPolicy(max_concurrency=2))
    active = 0
    peak_active = 0

    async def operation(number: int) -> int:
        nonlocal active, peak_active
        active += 1
        peak_active = max(peak_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        return number

    results = asyncio.run(
        runtime.execute_bounded([lambda number=number: operation(number) for number in range(5)])
    )

    assert results == [0, 1, 2, 3, 4]
    assert peak_active == 2


def test_failed_store_is_skipped_after_retry_and_agent_can_continue():
    repository = MockRestaurantRepository.package_second_store()
    repository.set_product_failures("S1", [RuntimeError("temporary failure"), RuntimeError("temporary failure")])
    app = create_demo_app(
        FakeScenario.PACKAGE_SECOND_STORE,
        repository=repository,
        policy=AgentPolicy(retry_count=1),
    )

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "SUCCESS"
    assert run.response.store_id == "S2"
    assert repository.product_call_counts["S1"] == 2
    assert run.state.failed_store_ids == ["S1"]


def test_all_timed_out_stores_return_controlled_no_result():
    repository = MockRestaurantRepository.package_second_store()
    for store_id in ("S1", "S2", "S3", "S4", "S5"):
        repository.set_product_delays(store_id, [0.02])
    app = create_demo_app(
        FakeScenario.PACKAGE_SECOND_STORE,
        repository=repository,
        policy=AgentPolicy(tool_timeout_seconds=0.001, retry_count=0),
    )

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "NO_RESULT"
    assert run.response.products == []
    assert run.state.timed_out_store_ids == ["S1", "S2", "S3", "S4", "S5"]
