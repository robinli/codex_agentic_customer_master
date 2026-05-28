from datetime import datetime
from typing import Any
import uuid

from pydantic import BaseModel


class AgentSessionCreate(BaseModel):
    title: str | None = None


class AgentSessionRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AgentMessageCreate(BaseModel):
    message: str


class AgentMessageRead(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    role: str
    content: str
    tool_name: str | None
    tool_args: dict[str, Any] | None
    tool_result: dict[str, Any] | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ToolCallResult(BaseModel):
    tool_name: str
    status: str
    input: dict[str, Any] | None = None
    output: dict[str, Any] | None = None


class AgentResponse(BaseModel):
    message: str
    tool_calls: list[ToolCallResult]
    data: dict[str, Any] | None = None
