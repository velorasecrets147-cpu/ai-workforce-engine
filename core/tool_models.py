from enum import Enum

from pydantic import BaseModel, Field


class ToolStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    DISABLED = "DISABLED"


class ToolResult(BaseModel):
    success: bool
    tool_name: str
    message: str
    data: dict = Field(default_factory=dict)


class ToolDefinition(BaseModel):
    name: str
    description: str
    status: ToolStatus = ToolStatus.AVAILABLE