import json
from typing import Any

from pydantic import ValidationError

from agent_demo.agent.errors import StructuredOutputError
from agent_demo.dto.domain import RecommendationIntent


def recommendation_intent_json_schema() -> dict[str, Any]:
    """Expose the schema that a real structured-output adapter would use."""

    return RecommendationIntent.model_json_schema()


def parse_recommendation_intent(raw: Any) -> RecommendationIntent:
    try:
        if isinstance(raw, str):
            return RecommendationIntent.model_validate(json.loads(raw))
        return RecommendationIntent.model_validate(raw)
    except (json.JSONDecodeError, ValidationError, TypeError) as error:
        raise StructuredOutputError("final output does not match RecommendationIntent") from error

