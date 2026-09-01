from typing import Protocol


class RetrievalService(Protocol):
    """RAG extension point: return candidate IDs, never authoritative live facts."""

    async def retrieve_candidate_ids(self, query: str) -> list[str]: ...

