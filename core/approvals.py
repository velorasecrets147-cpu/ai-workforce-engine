from core.models import (
    ApprovalRequest,
    ApprovalStatus,
    RiskLevel,
)


class ApprovalManager:

    def create_request(
        self,
        approval_id: str,
        task_id: str,
        description: str,
        risk_level: RiskLevel,
    ) -> ApprovalRequest:

        return ApprovalRequest(
            approval_id=approval_id,
            task_id=task_id,
            description=description,
            risk_level=risk_level,
        )

    def approve(self, request: ApprovalRequest) -> ApprovalRequest:
        request.status = ApprovalStatus.APPROVED
        return request

    def reject(self, request: ApprovalRequest) -> ApprovalRequest:
        request.status = ApprovalStatus.REJECTED
        return request