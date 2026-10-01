from core.approvals import ApprovalManager
from core.models import (
    ApprovalStatus,
    BusinessContext,
    WorkflowRun,
    WorkflowStatus,
    WorkflowTask,
)
from core.permissions import PermissionManager


class WorkflowOrchestrator:

    def __init__(self):
        self.permission_manager = PermissionManager()
        self.approval_manager = ApprovalManager()

    def create_run(
        self,
        run_id: str,
        workflow_name: str,
        business_context: BusinessContext,
    ) -> WorkflowRun:

        return WorkflowRun(
            run_id=run_id,
            workflow_name=workflow_name,
            business_context=business_context,
        )

    def start_run(
        self,
        workflow_run: WorkflowRun,
    ) -> WorkflowRun:

        if workflow_run.status != WorkflowStatus.PENDING:
            raise ValueError(
                "Workflow can only be started from PENDING status."
            )

        workflow_run.status = WorkflowStatus.RUNNING

        return workflow_run

    def prepare_task(
        self,
        workflow_run: WorkflowRun,
        task: WorkflowTask,
    ) -> WorkflowRun:

        if workflow_run.status not in {
            WorkflowStatus.RUNNING,
            WorkflowStatus.WAITING_FOR_APPROVAL,
        }:
            raise ValueError(
                "Workflow must be RUNNING before preparing a task."
            )

        workflow_run.current_task = task.task_id

        requires_approval = (
            self.permission_manager.requires_approval(
                task.risk_level,
                task.requires_human_approval,
            )
        )

        if requires_approval:

            approval = self.approval_manager.create_request(
                approval_id=f"{workflow_run.run_id}:{task.task_id}",
                task_id=task.task_id,
                description=task.description,
                risk_level=task.risk_level,
            )

            workflow_run.status = WorkflowStatus.WAITING_FOR_APPROVAL
            workflow_run.approval_request = approval

        else:

            workflow_run.status = WorkflowStatus.RUNNING
            workflow_run.approval_request = None

        return workflow_run

    def approve_current_task(
        self,
        workflow_run: WorkflowRun,
    ) -> WorkflowRun:

        if workflow_run.approval_request is None:
            raise ValueError(
                "No pending approval request exists."
            )

        if (
            workflow_run.approval_request.status
            != ApprovalStatus.PENDING
        ):
            raise ValueError(
                "Approval request is no longer pending."
            )

        self.approval_manager.approve(
            workflow_run.approval_request
        )

        workflow_run.status = WorkflowStatus.RUNNING

        return workflow_run

    def reject_current_task(
        self,
        workflow_run: WorkflowRun,
    ) -> WorkflowRun:

        if workflow_run.approval_request is None:
            raise ValueError(
                "No pending approval request exists."
            )

        if (
            workflow_run.approval_request.status
            != ApprovalStatus.PENDING
        ):
            raise ValueError(
                "Approval request is no longer pending."
            )

        self.approval_manager.reject(
            workflow_run.approval_request
        )

        workflow_run.status = WorkflowStatus.FAILED

        return workflow_run

    def complete_current_task(
        self,
        workflow_run: WorkflowRun,
        results: dict | None = None,
    ) -> WorkflowRun:

        if workflow_run.status != WorkflowStatus.RUNNING:
            raise ValueError(
                "Workflow must be RUNNING before completing a task."
            )

        if results:
            workflow_run.results.update(results)

        workflow_run.current_task = None
        workflow_run.status = WorkflowStatus.COMPLETED

        return workflow_run

    def complete_run(
        self,
        workflow_run: WorkflowRun,
        results: dict,
    ) -> WorkflowRun:

        return self.complete_current_task(
            workflow_run,
            results,
        )