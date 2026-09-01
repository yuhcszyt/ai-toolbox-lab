from agent_demo.dto.domain import Product
from agent_demo.repositories.mock_repository import MockRestaurantRepository


class ProductService:
    def __init__(self, repository: MockRestaurantRepository) -> None:
        self._repository = repository

    async def search_products(self, store_id: str) -> list[Product]:
        return await self._repository.list_products(store_id)

