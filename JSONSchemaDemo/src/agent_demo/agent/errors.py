class AgentRuntimeError(Exception):
    """Base class for expected, caller-safe runtime failures."""


class ToolExecutionError(AgentRuntimeError):
    pass


class InvalidToolCallError(AgentRuntimeError):
    pass


class ToolTimeoutError(ToolExecutionError):
    pass


class ToolBudgetExceededError(AgentRuntimeError):
    pass


class LoopLimitExceededError(AgentRuntimeError):
    pass


class StructuredOutputError(AgentRuntimeError):
    pass


class EvidenceValidationError(AgentRuntimeError):
    pass


class BusinessValidationError(AgentRuntimeError):
    pass
