import asyncio

from agent_demo.app import create_demo_app
from agent_demo.llm.fake import FakeScenario


def test_hallucinated_product_id_is_rejected_before_response_assembly():
    app = create_demo_app(FakeScenario.HALLUCINATED_ID)

    run = asyncio.run(
        app.run(
            user_query="找一家两人川菜套餐。",
            lat=31.2304,
            lng=121.4737,
        )
    )

    assert run.response.status == "FAILED"
    assert "P9999" not in run.state.evidence.products
    assert all(product.product_id != "P9999" for product in run.response.products)
    assert any(message["type"] == "validation_failure" for message in run.state.messages)


def test_display_fact_hallucinations_do_not_override_trusted_repository_data():
    app = create_demo_app(FakeScenario.ALTERED_DISPLAY_FACTS)

    run = asyncio.run(
        app.run(
            user_query="找一家两人川菜套餐。",
            lat=31.2304,
            lng=121.4737,
        )
    )

    assert run.response.status == "SUCCESS"
    assert run.response.store_name == "锦城川菜"
    assert run.response.products[0].name == "双人川味套餐"
    assert run.response.products[0].price == 128
