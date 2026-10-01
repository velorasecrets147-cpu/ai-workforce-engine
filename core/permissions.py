from core.models import RiskLevel


class PermissionManager:

    def requires_approval(
        self,
        risk_level: RiskLevel,
        explicitly_requires_approval: bool = False,
    ) -> bool:

        if explicitly_requires_approval:
            return True

        return risk_level == RiskLevel.HIGH