from enum import Enum

from pydantic import BaseModel, Field

from core.models import RiskLevel


class ActionType(str, Enum):
    NO_ACTION = "NO_ACTION"
    REQUEST_MORE_INFORMATION = "REQUEST_MORE_INFORMATION"
    HUMAN_REVIEW = "HUMAN_REVIEW"
    CREATE_OUTREACH = "CREATE_OUTREACH"


class ActionStatus(str, Enum):
    PLANNED = "PLANNED"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    READY = "READY"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class PlannedAction(BaseModel):
    action_id: str
    action_type: ActionType
    description: str
    risk_level: RiskLevel
    requires_human_approval: bool = False
    tool_name: str | None = None
    status: ActionStatus = ActionStatus.PLANNED
    parameters: dict = Field(default_factory=dict)


class ActionPlan(BaseModel):
    plan_id: str
    workflow_run_id: str
    actions: list[PlannedAction] = Field(default_factory=list)