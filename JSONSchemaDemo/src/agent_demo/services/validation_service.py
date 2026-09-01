from agent_demo.dto.domain import Product, RecommendationIntent, Store
from agent_demo.repositories.mock_repository import MockRestaurantRepository
from agent_demo.validation.business import validate_business


class ValidationService:
    """Reload selected facts from the live repository before responding."""

    def __init__(self, repository: MockRestaurantRepository) -> None:
        self._repository = repository

    async def revalidate(
        self, intent: RecommendationIntent, people_count: int
    ) -> tuple[Store, list[Product]]:
        store = await self._repository.get_store(intent.store_id)
        products = [await self._repository.get_product(product_id) for product_id in intent.product_ids]
        validate_business(intent, store, products, people_count)
        assert store is not None
        return store, [product for product in products if product is not None]

