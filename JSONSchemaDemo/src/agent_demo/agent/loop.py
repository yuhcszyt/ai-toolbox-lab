import asyncio

from agent_demo.agent.models import FinalAnswerAction, ToolCallAction
from agent_demo.agent.errors import (
    AgentRuntimeError,
    BusinessValidationError,
    EvidenceValidationError,
    StructuredOutputError,
    ToolExecutionError,
    ToolTimeoutError,
)
from agent_demo.agent.runtime import AgentRuntime
from agent_demo.agent.state import AgentState
from agent_demo.dto.response import RecommendedProduct, RecommendationResponse
from agent_demo.llm.base import LLMClient
from agent_demo.observability.tracing import TraceRecorder
from agent_demo.services.validation_service import ValidationService
from agent_demo.validation.evidence import validate_evidence
from agent_demo.validation.output import parse_recommendation_intent


class AgentLoop:
    def __init__(
        self,
        llm: LLMClient,
        runtime: AgentRuntime,
        validation_service: ValidationService,
        tracer: TraceRecorder,
    ) -> None:
        self._llm = llm
        self._runtime = runtime
        self._validation_service = validation_service
        self._tracer = tracer

    async def run(self, state: AgentState) -> RecommendationResponse:
        self._tracer.emit(state, "loop_started", loop_count=state.loop_count)
        try:
            async with asyncio.timeout(self._runtime.policy.total_deadline_seconds):
                response = await self._run_until_complete(state)
        except TimeoutError:
            state.messages.append(
                {"type": "runtime_failure", "detail": "total request deadline exceeded"}
            )
            response = RecommendationResponse(
                status="FAILED", warnings=["total request deadline exceeded"]
            )
        self._tracer.emit(
            state,
            "final_status",
            status=response.status,
            loop_count=state.loop_count,
            tool_call_count=state.tool_call_count,
        )
        return response

    async def _run_until_complete(self, state: AgentState) -> RecommendationResponse:
        try:
            while state.loop_count < self._runtime.policy.max_loop_count:
                state.loop_count += 1
                action = await self._llm.decide_next_action(state)
                self._tracer.emit(
                    state,
                    "llm_action",
                    action_type=action.type,
                    loop_count=state.loop_count,
                )
                if isinstance(action, FinalAnswerAction):
                    return await self._build_final_response(state)
                if isinstance(action, ToolCallAction):
                    try:
                        await self._runtime.execute_tool(action, state)
                    except ToolTimeoutError as error:
                        store_id = action.arguments.get("store_id")
                        if isinstance(store_id, str) and store_id not in state.timed_out_store_ids:
                            state.timed_out_store_ids.append(store_id)
                        state.messages.append(
                            {"type": "tool_timeout", "detail": str(error)}
                        )
                        self._tracer.emit(state, "tool_timeout", tool_name=action.tool_name)
                    except ToolExecutionError as error:
                        store_id = action.arguments.get("store_id")
                        if isinstance(store_id, str) and store_id not in state.failed_store_ids:
                            state.failed_store_ids.append(store_id)
                        state.messages.append(
                            {"type": "tool_failure", "detail": str(error)}
                        )
                        self._tracer.emit(state, "tool_failure", tool_name=action.tool_name)
                    continue
                return RecommendationResponse(status="NO_RESULT", warnings=[action.question])
        except AgentRuntimeError as error:
            state.messages.append({"type": "runtime_failure", "detail": str(error)})
            return RecommendationResponse(status="FAILED", warnings=[str(error)])
        return RecommendationResponse(status="FAILED", warnings=["loop budget exhausted"])

    async def _build_final_response(self, state: AgentState) -> RecommendationResponse:
        has_recommendable_product = any(
            not product.is_package
            or (
                product.suitable_people is not None
                and product.suitable_people >= state.people_count
            )
            for product in state.evidence.products.values()
        )
        if not has_recommendable_product:
            return RecommendationResponse(
                status="NO_RESULT", warnings=["no product evidence available"]
            )
        feedback: str | None = None
        for _ in range(self._runtime.policy.max_output_repair_attempts + 1):
            try:
                intent = parse_recommendation_intent(
                    await self._llm.generate_final_intent(state, feedback)
                )
                validate_evidence(intent, state.evidence, state.people_count)
                store, trusted_products = await self._validation_service.revalidate(
                    intent, state.people_count
                )
            except (StructuredOutputError, EvidenceValidationError, BusinessValidationError) as error:
                feedback = str(error)
                state.messages.append(
                    {"type": "validation_failure", "detail": feedback}
                )
                self._tracer.emit(state, "validation_failure", detail=feedback)
                continue

            state.final_intent = intent
            state.selected_store_id = intent.store_id
            state.selected_product_ids = intent.product_ids
            return RecommendationResponse(
                status="SUCCESS",
                recommendation_type=intent.recommendation_type,
                store_id=store.store_id,
                store_name=store.name,
                products=[
                    RecommendedProduct(
                        product_id=product.product_id,
                        name=product.name,
                        price=product.price,
                    )
                    for product in trusted_products
                ],
                reason=intent.reason,
            )
        return RecommendationResponse(
            status="FAILED", warnings=["final output failed validation"]
        )
