from typing import Literal

from pydantic import BaseModel, Field


class RecommendedProduct(BaseModel):
    product_id: str
    name: str
    price: int


class RecommendationResponse(BaseModel):
    status: Literal["SUCCESS", "NO_RESULT", "PARTIAL_SUCCESS", "FAILED"]
    recommendation_type: Literal["PACKAGE", "SINGLE_ITEMS"] | None = None
    store_id: str | None = None
    store_name: str | None = None
    products: list[RecommendedProduct] = Field(default_factory=list)
    reason: str | None = None
    warnings: list[str] = Field(default_factory=list)

