import asyncio

from agent_demo.app import create_demo_app
from agent_demo.llm.fake import FakeScenario


def test_trace_records_runtime_decisions_without_hidden_reasoning():
    app = create_demo_app(FakeScenario.PACKAGE_SECOND_STORE)

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "SUCCESS"
    event_names = [event.name for event in app.tracer.events]
    assert "loop_started" in event_names
    assert "llm_action" in event_names
    assert "tool_finished" in event_names
    assert "final_status" in event_names
    assert all(event.request_id == run.state.request_id for event in app.tracer.events)
    assert all("chain_of_thought" not in event.data for event in app.tracer.events)
