from core.models import RiskLevel
from core.planning import PlannedAction


class PermissionManager:

    def requires_approval(
        self,
        risk_level: RiskLevel,
        explicitly_requires_approval: bool = False,
    ) -> bool:

        if explicitly_requires_approval:
            return True

        return risk_level == RiskLevel.HIGH

    def can_execute_tool(
        self,
        action: PlannedAction,
        approved: bool = False,
    ) -> bool:

        if action.requires_human_approval and not approved:
            return False

        if action.risk_level == RiskLevel.HIGH and not approved:
            return False

        return True