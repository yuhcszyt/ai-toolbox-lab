import json
import asyncio
import time
from collections.abc import Awaitable, Callable, Iterable
from typing import TypeVar

from pydantic import ValidationError

from agent_demo.agent.errors import (
    InvalidToolCallError,
    ToolBudgetExceededError,
    ToolExecutionError,
    ToolTimeoutError,
)
from agent_demo.agent.models import ToolCallAction
from agent_demo.agent.policy import AgentPolicy
from agent_demo.agent.state import AgentState
from agent_demo.observability.tracing import TraceRecorder
from agent_demo.tools.registry import ToolRegistry, ToolResult


ResultT = TypeVar("ResultT")


class AgentRuntime:
    def __init__(
        self,
        registry: ToolRegistry,
        policy: AgentPolicy,
        tracer: TraceRecorder | None = None,
    ) -> None:
        self._registry = registry
        self.policy = policy
        self._semaphore = asyncio.Semaphore(policy.max_concurrency)
        self._tracer = tracer

    async def execute_tool(self, action: ToolCallAction, state: AgentState) -> ToolResult:
        if state.tool_call_count >= self.policy.max_tool_calls:
            raise ToolBudgetExceededError("tool-call budget exhausted")
        tool = self._registry.get(action.tool_name)
        if tool is None:
            raise InvalidToolCallError(f"unknown tool: {action.tool_name}")
        try:
            normalized_arguments = tool.validate_arguments(action.arguments)
        except (ValidationError, TypeError, ValueError) as error:
            raise InvalidToolCallError(
                f"invalid arguments for {action.tool_name}"
            ) from error
        action = action.model_copy(update={"arguments": normalized_arguments})

        signature = self._tool_signature(action)
        executed_count = state.executed_tool_signatures.get(signature, 0)
        if executed_count > self.policy.max_same_tool_call_repeats:
            raise ToolBudgetExceededError("repeated tool call blocked by policy")
        if action.tool_name == "search_products":
            store_id = action.arguments.get("store_id")
            if not isinstance(store_id, str):
                raise InvalidToolCallError("search_products requires a store returned by a tool")
            if (
                store_id not in state.considered_store_ids
                and len(state.considered_store_ids) >= self.policy.max_stores
            ):
                raise ToolBudgetExceededError("max stores budget exhausted")
            if store_id not in state.evidence.stores:
                raise InvalidToolCallError("search_products requires a store returned by a tool")
            if store_id in state.timed_out_store_ids:
                raise InvalidToolCallError("timed-out store cannot be queried again")

        state.tool_call_count += 1
        state.executed_tool_signatures[signature] = executed_count + 1
        state.tool_calls.append(
            {"tool_name": action.tool_name, "arguments": action.arguments}
        )
        if action.tool_name == "search_products":
            store_id = action.arguments["store_id"]
            if store_id not in state.considered_store_ids:
                state.considered_store_ids.append(store_id)
        started_at = time.perf_counter()
        self._emit(state, "tool_started", tool_name=action.tool_name)
        result = await self._execute_with_retry(tool, action, state)
        self.record_tool_result(action, result, state)
        self._emit(
            state,
            "tool_finished",
            tool_name=action.tool_name,
            duration_ms=round((time.perf_counter() - started_at) * 1000, 2),
            result_count=len(result.stores) + len(result.products),
            evidence_stores=len(state.evidence.stores),
            evidence_products=len(state.evidence.products),
        )
        return result

    async def _execute_with_retry(
        self, tool, action: ToolCallAction, state: AgentState
    ) -> ToolResult:
        for attempt in range(self.policy.retry_count + 1):
            try:
                async with self._semaphore:
                    async with asyncio.timeout(self.policy.tool_timeout_seconds):
                        return await tool.execute(action.arguments, state)
            except TimeoutError as error:
                if attempt == self.policy.retry_count:
                    raise ToolTimeoutError(
                        f"tool timed out: {action.tool_name}"
                    ) from error
                state.messages.append(
                    {
                        "type": "tool_retry",
                        "tool_name": action.tool_name,
                        "attempt": attempt + 1,
                        "reason": "timeout",
                    }
                )
                self._emit(
                    state,
                    "tool_retry",
                    tool_name=action.tool_name,
                    attempt=attempt + 1,
                    reason="timeout",
                )
            except ValueError as error:
                raise InvalidToolCallError(
                    f"tool rejected arguments: {action.tool_name}"
                ) from error
            except ToolExecutionError:
                raise
            except Exception as error:
                if attempt == self.policy.retry_count:
                    raise ToolExecutionError(
                        f"tool execution failed: {action.tool_name}"
                    ) from error
                state.messages.append(
                    {
                        "type": "tool_retry",
                        "tool_name": action.tool_name,
                        "attempt": attempt + 1,
                        "reason": "execution_error",
                    }
                )
                self._emit(
                    state,
                    "tool_retry",
                    tool_name=action.tool_name,
                    attempt=attempt + 1,
                    reason="execution_error",
                )
        raise AssertionError("retry loop must return or raise")

    async def execute_bounded(
        self, operations: Iterable[Callable[[], Awaitable[ResultT]]]
    ) -> list[ResultT]:
        """Run independent operations using the same configured concurrency budget."""

        async def execute_one(operation: Callable[[], Awaitable[ResultT]]) -> ResultT:
            async with self._semaphore:
                return await operation()

        return await asyncio.gather(*(execute_one(operation) for operation in operations))

    def _emit(self, state: AgentState, name: str, **data) -> None:
        if self._tracer is not None:
            self._tracer.emit(state, name, **data)

    @staticmethod
    def _tool_signature(action: ToolCallAction) -> str:
        normalized_arguments = json.dumps(
            action.arguments, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str
        )
        return f"{action.tool_name}:{normalized_arguments}"

    def record_tool_result(
        self, action: ToolCallAction, result: ToolResult, state: AgentState
    ) -> None:
        state.tool_results.append(
            {
                "tool_name": action.tool_name,
                "store_count": len(result.stores),
                "product_count": len(result.products),
            }
        )
        if result.stores:
            state.stores.update({store.store_id: store for store in result.stores})
            state.evidence.record_stores(result.stores)
        if result.products:
            state.products.update({product.product_id: product for product in result.products})
            state.evidence.record_products(result.products)
        if action.tool_name == "search_products":
            store_id = action.arguments["store_id"]
            if store_id not in state.searched_store_ids:
                state.searched_store_ids.append(store_id)
