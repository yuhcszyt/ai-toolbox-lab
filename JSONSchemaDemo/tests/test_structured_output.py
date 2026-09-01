import asyncio

from agent_demo.app import create_demo_app
from agent_demo.llm.fake import FakeScenario
from agent_demo.validation.output import recommendation_intent_json_schema


def test_invalid_structured_output_is_repaired_once_then_accepted():
    app = create_demo_app(FakeScenario.INVALID_OUTPUT_ONCE)

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "SUCCESS"
    assert len([m for m in run.state.messages if m["type"] == "validation_failure"]) == 1
    assert "recommendation_type" in recommendation_intent_json_schema()["properties"]


def test_invalid_structured_output_twice_returns_controlled_failure():
    app = create_demo_app(FakeScenario.INVALID_OUTPUT_TWICE)

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "FAILED"
    assert len([m for m in run.state.messages if m["type"] == "validation_failure"]) == 2
    assert run.response.products == []
