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
    assert run.current_task == "outreach"
    assert run.approval_request is not None
    assert (
        run.approval_request.status
        == ApprovalStatus.PENDING
    )

    print("PASS")

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
    assert (
        run.approval_request.status
        == ApprovalStatus.APPROVED
    )

    print("PASS")

    print("\n========================================")
    print("TEST 3 — EXECUTION COMPLETES")
    print("========================================")

    orchestrator.complete_current_task(
        run,
        {
            "outreach_result": (
                "Simulated outreach completed."
            )
        },
    )

    print(f"Workflow status: {run.status}")
    print(f"Current task: {run.current_task}")
    print(f"Results: {run.results}")

    assert run.status == WorkflowStatus.COMPLETED
    assert run.current_task is None
    assert (
        run.results["outreach_result"]
        == "Simulated outreach completed."
    )

    print("PASS")

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
    assert (
        run.approval_request.status
        == ApprovalStatus.REJECTED
    )

    print("PASS")

    print("\n========================================")
    print("TEST 5 — EVALUATION")
    print("========================================")

    from evaluation.evaluator import WorkflowEvaluator

    evaluator = WorkflowEvaluator()

    evaluation = evaluator.evaluate(
        task_completed=True,
        output_quality=0.9,
        business_outcome="Outreach task completed",
    )

    print(
        f"Task completed: "
        f"{evaluation.task_completed}"
    )
    print(
        f"Output quality: "
        f"{evaluation.output_quality}"
    )
    print(
        f"Business outcome: "
        f"{evaluation.business_outcome}"
    )
    print(
        f"Improvement suggestions: "
        f"{evaluation.improvement_suggestions}"
    )

    assert evaluation.task_completed is True
    assert evaluation.output_quality == 0.9
    assert (
        evaluation.business_outcome
        == "Outreach task completed"
    )

    print("PASS")

    print("\n========================================")
    print("ALL ENGINE TESTS PASSED")
    print("========================================")


if __name__ == "__main__":
    main()