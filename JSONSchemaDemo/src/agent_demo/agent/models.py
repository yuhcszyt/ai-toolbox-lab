from typing import Any, Literal

from pydantic import BaseModel


class ToolCallAction(BaseModel):
    type: Literal["TOOL_CALL"] = "TOOL_CALL"
    tool_name: str
    arguments: dict[str, Any]


class FinalAnswerAction(BaseModel):
    type: Literal["FINAL_ANSWER"] = "FINAL_ANSWER"


class AskUserAction(BaseModel):
    type: Literal["ASK_USER"] = "ASK_USER"
    question: str


AgentAction = ToolCallAction | FinalAnswerAction | AskUserAction

