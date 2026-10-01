import uuid

from core.models import RiskLevel
from core.planning import (
    ActionPlan,
    ActionStatus,
    ActionType,
    PlannedAction,
)


class ActionPlanner:

    def create_plan(
        self,
        workflow_run_id: str,
        decision: str,
        decision_reason: str,
    ) -> ActionPlan:

        action_type = ActionType.NO_ACTION
        description = "No action required."
        risk_level = RiskLevel.LOW
        requires_approval = False
        tool_name = None

        if decision == "QUALIFY":
            action_type = ActionType.CREATE_OUTREACH
            description = (
                "Prepare outreach for the qualified company."
            )
            risk_level = RiskLevel.HIGH
            requires_approval = True
            tool_name = "email"

        elif decision == "NEED_MORE_INFORMATION":
            action_type = ActionType.REQUEST_MORE_INFORMATION
            description = (
                "Request additional information before "
                "continuing the workflow."
            )
            risk_level = RiskLevel.MEDIUM
            requires_approval = False

        elif decision == "HUMAN_REVIEW":
            action_type = ActionType.HUMAN_REVIEW
            description = (
                "Send the workflow decision to a human "
                "for review."
            )
            risk_level = RiskLevel.HIGH
            requires_approval = True

        elif decision == "REJECT":
            action_type = ActionType.NO_ACTION
            description = (
                "No further action should be taken "
                "for this company."
            )
            risk_level = RiskLevel.LOW
            requires_approval = False

        action = PlannedAction(
            action_id=str(uuid.uuid4()),
            action_type=action_type,
            description=description,
            risk_level=risk_level,
            requires_human_approval=requires_approval,
            tool_name=tool_name,
            status=(
                ActionStatus.WAITING_FOR_APPROVAL
                if requires_approval
                else ActionStatus.READY
            ),
            parameters={
                "decision": decision,
                "decision_reason": decision_reason,
            },
        )

        return ActionPlan(
            plan_id=str(uuid.uuid4()),
            workflow_run_id=workflow_run_id,
            actions=[action],
        )