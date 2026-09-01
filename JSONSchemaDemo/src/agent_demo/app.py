from dataclasses import dataclass
from uuid import uuid4

from agent_demo.agent.loop import AgentLoop
from agent_demo.agent.policy import AgentPolicy
from agent_demo.agent.runtime import AgentRuntime
from agent_demo.agent.state import AgentState
from agent_demo.dto.response import RecommendationResponse
from agent_demo.llm.fake import FakeLLM, FakeScenario
from agent_demo.observability.tracing import TraceRecorder
from agent_demo.repositories.mock_repository import MockRestaurantRepository
from agent_demo.services.product_service import ProductService
from agent_demo.services.store_service import StoreService
from agent_demo.services.validation_service import ValidationService
from agent_demo.tools.product_tool import ProductSearchTool
from agent_demo.tools.registry import ToolRegistry
from agent_demo.tools.store_tool import StoreSearchTool


@dataclass
class AgentRun:
    response: RecommendationResponse
    state: AgentState


class AgentDemoApp:
    def __init__(
        self,
        repository: MockRestaurantRepository,
        llm: FakeLLM,
        policy: AgentPolicy | None = None,
    ) -> None:
        self.repository = repository
        self.policy = policy or AgentPolicy()
        self.tracer = TraceRecorder()
        registry = ToolRegistry(
            [
                StoreSearchTool(StoreService(repository), self.policy.max_stores),
                ProductSearchTool(ProductService(repository)),
            ]
        )
        self._loop = AgentLoop(
            llm,
            AgentRuntime(registry, self.policy, self.tracer),
            ValidationService(repository),
            self.tracer,
        )

    async def run(
        self,
        user_query: str,
        lat: float,
        lng: float,
        category: str = "川菜",
        people_count: int = 2,
    ) -> AgentRun:
        request_id = str(uuid4())
        state = AgentState(
            request_id=request_id,
            session_id=request_id,
            user_query=user_query,
            lat=lat,
            lng=lng,
            category=category,
            people_count=people_count,
        )
        return AgentRun(response=await self._loop.run(state), state=state)


def create_demo_app(
    scenario: FakeScenario = FakeScenario.PACKAGE_SECOND_STORE,
    repository: MockRestaurantRepository | None = None,
    policy: AgentPolicy | None = None,
) -> AgentDemoApp:
    if repository is None:
        if scenario is FakeScenario.NO_PACKAGE:
            repository = MockRestaurantRepository.no_package()
        elif scenario is FakeScenario.PACKAGE_FIRST_STORE:
            repository = MockRestaurantRepository.package_first_store()
        else:
            repository = MockRestaurantRepository.package_second_store()
    return AgentDemoApp(
        repository=repository,
        llm=FakeLLM(scenario),
        policy=policy,
    )
