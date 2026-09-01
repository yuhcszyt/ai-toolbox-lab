from pydantic import BaseModel


class AgentPolicy(BaseModel):
    max_loop_count: int = 12
    max_tool_calls: int = 10
    max_stores: int = 5
    tool_timeout_seconds: float = 2.0
    retry_count: int = 1
    max_concurrency: int = 3
    total_deadline_seconds: float = 8.0
    max_same_tool_call_repeats: int = 1
    max_output_repair_attempts: int = 1

