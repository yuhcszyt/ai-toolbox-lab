from agent_demo.agent.errors import EvidenceValidationError
from agent_demo.agent.state import EvidenceStore
from agent_demo.dto.domain import RecommendationIntent


def validate_evidence(
    intent: RecommendationIntent, evidence: EvidenceStore, people_count: int
) -> None:
    store = evidence.stores.get(intent.store_id)
    if store is None:
        raise EvidenceValidationError("selected store was not returned by a tool")

    for product_id in intent.product_ids:
        product = evidence.products.get(product_id)
        if product is None:
            raise EvidenceValidationError("selected product was not returned by a tool")
        if product.store_id != intent.store_id:
            raise EvidenceValidationError("selected product does not belong to selected store")
        if intent.recommendation_type == "PACKAGE" and (
            not product.is_package
            or product.suitable_people is None
            or product.suitable_people < people_count
        ):
            raise EvidenceValidationError("selected package is not suitable for requested people count")

