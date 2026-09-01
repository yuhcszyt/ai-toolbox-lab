import asyncio

from agent_demo.app import create_demo_app
from agent_demo.llm.fake import FakeScenario
from agent_demo.repositories.mock_repository import MockRestaurantRepository


def test_business_revalidation_rejects_product_that_became_unavailable():
    repository = MockRestaurantRepository.package_second_store()
    repository.make_product_unavailable_on_next_validation_read("P2001")
    app = create_demo_app(FakeScenario.PACKAGE_SECOND_STORE, repository=repository)

    run = asyncio.run(
        app.run("找两人川菜套餐。", lat=31.2304, lng=121.4737)
    )

    assert run.response.status == "FAILED"
    assert all(product.product_id != "P2001" for product in run.response.products)
    assert any(message["type"] == "validation_failure" for message in run.state.messages)
