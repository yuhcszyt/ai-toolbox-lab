from typing import Any, Protocol


class UserProfileRepository(Protocol):
    """Optional long-term memory boundary; it is intentionally unused by this MVP."""

    async def get_profile(self, user_id: str) -> dict[str, Any] | None: ...

