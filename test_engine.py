from core.models import (
    ApprovalStatus,
    BusinessContext,
    RiskLevel,
    WorkflowStatus,
    WorkflowTask,
)
from core.orchestrator import WorkflowOrchestrator


def create_workflow():

    business = BusinessContext(
        business_name="Demo Business",
        business_type="B2B Service",
        process_name="Client Acquisition",
        goals=[
            "Find qualified companies",
            "Identify business needs",
        ],
        constraints=[
            "Do not contact companies without approval",
        ],
    )

    orchestrator = WorkflowOrchestrator()

    run = orchestrator.create_run(
        run_id="run-001",
        workflow_name="client_acquisition",
        business_context=business,
    )

    orchestrator.start_run(run)

    outreach_task = WorkflowTask(
        task_id="outreach",
        name="Client Outreach",
        description="Send outreach to a qualified company.",
        risk_level=RiskLevel.HIGH,
        requires_human_approval=True,
    )

    orchestrator.prepare_task(
        run,
        outreach_task,
    )

    return orchestrator, run


def main():

    # ============================================
    # TEST 1 — APPROVAL REQUEST
    # ============================================

    print("========================================")
    print("TEST 1 — APPROVAL REQUEST")
    print("========================================")

    orchestrator, run = create_workflow()

    print(f"Workflow status: {run.status}")
    print(f"Current task: {run.current_task}")
    print(
        f"Approval status: "
        f"{run.approval_request.status}"
    )

    assert run.status == WorkflowStatus.WAITING_FOR_APPROVAL
    assert run.approval_request.status == ApprovalStatus.PENDING

    print("PASS")


    # ============================================
    # TEST 2 — HUMAN APPROVES
    # ============================================

    print("\n========================================")
    print("TEST 2 — HUMAN APPROVES")
    print("========================================")

    orchestrator.approve_current_task(run)

    print(f"Workflow status: {run.status}")
    print(
        f"Approval status: "
        f"{run.approval_request.status}"
    )

    assert run.status == WorkflowStatus.RUNNING
    assert run.approval_request.status == ApprovalStatus.APPROVED

    print("PASS")


    # ============================================
    # TEST 3 — EXECUTION COMPLETES
    # ============================================

    print("\n========================================")
    print("TEST 3 — EXECUTION COMPLETES")
    print("========================================")

    orchestrator.complete_current_task(
        run,
        {
            "outreach_result": "Simulated outreach completed."
        },
    )

    print(f"Workflow status: {run.status}")
    print(f"Current task: {run.current_task}")
    print(f"Results: {run.results}")

    assert run.status == WorkflowStatus.COMPLETED
    assert run.current_task is None

    print("PASS")


    # ============================================
    # TEST 4 — HUMAN REJECTS
    # ============================================

    print("\n========================================")
    print("TEST 4 — HUMAN REJECTS")
    print("========================================")

    orchestrator, run = create_workflow()

    orchestrator.reject_current_task(run)

    print(f"Workflow status: {run.status}")
    print(
        f"Approval status: "
        f"{run.approval_request.status}"
    )

    assert run.status == WorkflowStatus.FAILED
    assert run.approval_request.status == ApprovalStatus.REJECTED

    print("PASS")


    # ============================================
    # FINAL
    # ============================================

    print("\n========================================")
    print("ALL ENGINE TESTS PASSED")
    print("========================================")


if __name__ == "__main__":
    main()