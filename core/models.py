from enum import Enum

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class WorkflowStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_FOR_APPROVAL = "WAITING_FOR_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class BusinessContext(BaseModel):
    business_name: str
    business_type: str
    process_name: str
    goals: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)


class WorkflowTask(BaseModel):
    task_id: str
    name: str
    description: str
    risk_level: RiskLevel = RiskLevel.LOW
    requires_human_approval: bool = False


class ApprovalRequest(BaseModel):
    approval_id: str
    task_id: str
    description: str
    risk_level: RiskLevel
    status: ApprovalStatus = ApprovalStatus.PENDING


class WorkflowRun(BaseModel):
    run_id: str
    workflow_name: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    business_context: BusinessContext
    current_task: str | None = None
    results: dict = Field(default_factory=dict)
    approval_request: ApprovalRequest | None = None