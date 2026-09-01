from agent_demo.dto.domain import Store
from agent_demo.repositories.mock_repository import MockRestaurantRepository


class StoreService:
    def __init__(self, repository: MockRestaurantRepository) -> None:
        self._repository = repository

    async def search_nearby(
        self, lat: float, lng: float, category: str, limit: int
    ) -> list[Store]:
        if not -90 <= lat <= 90 or not -180 <= lng <= 180:
            raise ValueError("location is outside valid latitude/longitude bounds")
        if not category.strip():
            raise ValueError("category is required")
        stores = await self._repository.list_stores(category)
        return sorted(stores, key=lambda store: store.distance_meters)[:limit]

