from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Store(BaseModel):
    store_id: str
    name: str
    category: str
    rating: float
    distance_meters: int
    available: bool = True


class Product(BaseModel):
    product_id: str
    store_id: str
    name: str
    price: int
    is_package: bool
    suitable_people: int | None = None
    available: bool = True


class RecommendationIntent(BaseModel):
    """LLM-selected IDs and explanation, before trusted response assembly."""

    model_config = ConfigDict(extra="ignore")

    recommendation_type: Literal["PACKAGE", "SINGLE_ITEMS"]
    store_id: str
    product_ids: list[str] = Field(min_length=1)
    reason: str = Field(min_length=1)

