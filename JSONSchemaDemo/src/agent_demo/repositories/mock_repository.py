from collections import defaultdict
import asyncio

from agent_demo.dto.domain import Product, Store


class MockRestaurantRepository:
    """In-memory source of truth for the deterministic demo."""

    def __init__(self, stores: list[Store], products: list[Product]) -> None:
        self._stores = {store.store_id: store for store in stores}
        self._products = {product.product_id: product for product in products}
        self.product_call_counts: defaultdict[str, int] = defaultdict(int)
        self._product_delays: defaultdict[str, list[float]] = defaultdict(list)
        self._product_failures: defaultdict[str, list[Exception]] = defaultdict(list)
        self._unavailable_on_next_product_read: set[str] = set()

    @classmethod
    def package_second_store(cls) -> "MockRestaurantRepository":
        stores = [
            Store(store_id="S1", name="川味小馆", category="川菜", rating=4.7, distance_meters=180),
            Store(store_id="S2", name="锦城川菜", category="川菜", rating=4.8, distance_meters=420),
            Store(store_id="S3", name="远山川菜", category="川菜", rating=4.9, distance_meters=700),
            Store(store_id="S4", name="巷口川菜", category="川菜", rating=4.5, distance_meters=860),
            Store(store_id="S5", name="巴蜀人家", category="川菜", rating=4.6, distance_meters=1100),
        ]
        products = [
            Product(product_id="P1001", store_id="S1", name="麻婆豆腐", price=38, is_package=False),
            Product(product_id="P1002", store_id="S1", name="回锅肉", price=48, is_package=False),
            Product(product_id="P2001", store_id="S2", name="双人川味套餐", price=128, is_package=True, suitable_people=2),
            Product(product_id="P2002", store_id="S2", name="水煮牛肉", price=88, is_package=False),
            Product(product_id="P3001", store_id="S3", name="双人招牌套餐", price=138, is_package=True, suitable_people=2),
            Product(product_id="P4001", store_id="S4", name="夫妻肺片", price=46, is_package=False),
            Product(product_id="P5001", store_id="S5", name="宫保鸡丁", price=52, is_package=False),
        ]
        return cls(stores, products)

    @classmethod
    def no_package(cls) -> "MockRestaurantRepository":
        base = cls.package_second_store()
        return cls(
            list(base._stores.values()),
            [
                product.model_copy(update={"is_package": False, "suitable_people": None})
                for product in base._products.values()
            ],
        )

    @classmethod
    def package_first_store(cls) -> "MockRestaurantRepository":
        base = cls.package_second_store()
        return cls(
            list(base._stores.values()),
            [
                product.model_copy(update={"is_package": True, "suitable_people": 2})
                if product.product_id == "P1001"
                else product
                for product in base._products.values()
            ],
        )

    async def list_stores(self, category: str) -> list[Store]:
        return [
            store.model_copy(deep=True)
            for store in self._stores.values()
            if store.category == category and store.available
        ]

    async def list_products(self, store_id: str) -> list[Product]:
        self.product_call_counts[store_id] += 1
        delays = self._product_delays[store_id]
        delay = delays.pop(0) if delays else 0.0
        if delay:
            await asyncio.sleep(delay)
        failures = self._product_failures[store_id]
        if failures:
            raise failures.pop(0)
        return [
            product.model_copy(deep=True)
            for product in self._products.values()
            if product.store_id == store_id and product.available
        ]

    async def get_store(self, store_id: str) -> Store | None:
        store = self._stores.get(store_id)
        return store.model_copy(deep=True) if store else None

    async def get_product(self, product_id: str) -> Product | None:
        if product_id in self._unavailable_on_next_product_read:
            self._unavailable_on_next_product_read.remove(product_id)
            self._products[product_id] = self._products[product_id].model_copy(
                update={"available": False}
            )
        product = self._products.get(product_id)
        return product.model_copy(deep=True) if product else None

    def make_product_unavailable_on_next_validation_read(self, product_id: str) -> None:
        self._unavailable_on_next_product_read.add(product_id)

    def set_product_delays(self, store_id: str, delays: list[float]) -> None:
        self._product_delays[store_id] = list(delays)

    def set_product_failures(self, store_id: str, failures: list[Exception]) -> None:
        self._product_failures[store_id] = list(failures)
