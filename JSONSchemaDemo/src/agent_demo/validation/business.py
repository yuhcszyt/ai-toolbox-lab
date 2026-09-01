from agent_demo.agent.errors import BusinessValidationError
from agent_demo.dto.domain import Product, RecommendationIntent, Store


def validate_business(
    intent: RecommendationIntent,
    store: Store | None,
    products: list[Product | None],
    people_count: int,
) -> None:
    if store is None or not store.available:
        raise BusinessValidationError("selected store is no longer available")
    if any(product is None or not product.available for product in products):
        raise BusinessValidationError("selected product is no longer available")

    live_products = [product for product in products if product is not None]
    if any(product.store_id != store.store_id for product in live_products):
        raise BusinessValidationError("selected product no longer belongs to selected store")
    if intent.recommendation_type == "PACKAGE" and any(
        not product.is_package
        or product.suitable_people is None
        or product.suitable_people < people_count
        for product in live_products
    ):
        raise BusinessValidationError("selected package no longer satisfies people count")

