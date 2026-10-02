from core.action_planner import ActionPlanner
from core.models import (
    ApprovalStatus,
    BusinessContext,
    RiskLevel,
    WorkflowStatus,
    WorkflowTask,
)
from core.planning import (
    ActionStatus,
    ActionType,
)
from core.orchestrator import WorkflowOrchestrator
from evaluation.evaluator import WorkflowEvaluator


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

    # =========================================================
    # TEST 1 — APPROVAL REQUEST
    # =========================================================

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

    # =========================================================
    # TEST 2 — HUMAN APPROVES
    # =========================================================

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

    # =========================================================
    # TEST 3 — EXECUTION COMPLETES
    # =========================================================

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

    # =========================================================
    # TEST 4 — HUMAN REJECTS
    # =========================================================

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

    # =========================================================
    # TEST 5 — EVALUATION
    # =========================================================

    print("\n========================================")
    print("TEST 5 — EVALUATION")
    print("========================================")

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

    # =========================================================
    # TEST 6 — ACTION PLANNER QUALIFY
    # =========================================================

    print("\n========================================")
    print("TEST 6 — ACTION PLANNER QUALIFY")
    print("========================================")

    planner = ActionPlanner()

    action_plan = planner.create_plan(
        workflow_run_id="run-001",
        decision="QUALIFY",
        decision_reason=(
            "Company matches the qualification criteria."
        ),
    )

    action = action_plan.actions[0]

    print(f"Plan ID: {action_plan.plan_id}")
    print(f"Action type: {action.action_type}")
    print(f"Description: {action.description}")
    print(f"Risk level: {action.risk_level}")
    print(
        f"Human approval required: "
        f"{action.requires_human_approval}"
    )
    print(f"Tool: {action.tool_name}")
    print(f"Status: {action.status}")

    assert len(action_plan.actions) == 1
    assert (
        action.action_type
        == ActionType.CREATE_OUTREACH
    )
    assert action.risk_level == RiskLevel.HIGH
    assert action.requires_human_approval is True
    assert action.tool_name == "email"
    assert (
        action.status
        == ActionStatus.WAITING_FOR_APPROVAL
    )

    print("PASS")

    # =========================================================
    # TEST 7 — ACTION PLANNER REJECT
    # =========================================================

    print("\n========================================")
    print("TEST 7 — ACTION PLANNER REJECT")
    print("========================================")

    reject_plan = planner.create_plan(
        workflow_run_id="run-002",
        decision="REJECT",
        decision_reason=(
            "Company does not match the criteria."
        ),
    )

    reject_action = reject_plan.actions[0]

    print(f"Action type: {reject_action.action_type}")
    print(f"Risk level: {reject_action.risk_level}")
    print(
        f"Human approval required: "
        f"{reject_action.requires_human_approval}"
    )
    print(f"Status: {reject_action.status}")

    assert (
        reject_action.action_type
        == ActionType.NO_ACTION
    )
    assert reject_action.risk_level == RiskLevel.LOW
    assert reject_action.requires_human_approval is False
    assert reject_action.tool_name is None
    assert reject_action.status == ActionStatus.READY

    print("PASS")

    # =========================================================
    # TEST 8 — ACTION PLANNER NEED MORE INFORMATION
    # =========================================================

    print("\n========================================")
    print("TEST 8 — ACTION PLANNER NEED MORE INFORMATION")
    print("========================================")

    information_plan = planner.create_plan(
        workflow_run_id="run-003",
        decision="NEED_MORE_INFORMATION",
        decision_reason=(
            "Important qualification information is missing."
        ),
    )

    information_action = information_plan.actions[0]

    print(
        f"Action type: "
        f"{information_action.action_type}"
    )
    print(
        f"Risk level: "
        f"{information_action.risk_level}"
    )
    print(
        f"Human approval required: "
        f"{information_action.requires_human_approval}"
    )
    print(
        f"Status: "
        f"{information_action.status}"
    )

    assert (
        information_action.action_type
        == ActionType.REQUEST_MORE_INFORMATION
    )
    assert information_action.risk_level == RiskLevel.MEDIUM
    assert information_action.requires_human_approval is False
    assert information_action.tool_name is None
    assert information_action.status == ActionStatus.READY

    print("PASS")

    # =========================================================
    # TEST 9 — ACTION PLANNER HUMAN REVIEW
    # =========================================================

    print("\n========================================")
    print("TEST 9 — ACTION PLANNER HUMAN REVIEW")
    print("========================================")

    review_plan = planner.create_plan(
        workflow_run_id="run-004",
        decision="HUMAN_REVIEW",
        decision_reason=(
            "Conflicting information requires human judgment."
        ),
    )

    review_action = review_plan.actions[0]

    print(
        f"Action type: "
        f"{review_action.action_type}"
    )
    print(
        f"Risk level: "
        f"{review_action.risk_level}"
    )
    print(
        f"Human approval required: "
        f"{review_action.requires_human_approval}"
    )
    print(
        f"Status: "
        f"{review_action.status}"
    )

    assert (
        review_action.action_type
        == ActionType.HUMAN_REVIEW
    )
    assert review_action.risk_level == RiskLevel.HIGH
    assert review_action.requires_human_approval is True
    assert review_action.tool_name is None
    assert (
        review_action.status
        == ActionStatus.WAITING_FOR_APPROVAL
    )

    print("PASS")

    # =========================================================
    # TEST 10 — ACTION PLAN WORKFLOW INTEGRATION
    # =========================================================

    print("\n========================================")
    print("TEST 10 — ACTION PLAN WORKFLOW INTEGRATION")
    print("========================================")

    integration_run = orchestrator.create_run(
        run_id="run-integration",
        workflow_name="client_acquisition",
        business_context=BusinessContext(
            business_name="Demo Business",
            business_type="B2B Service",
            process_name="Client Acquisition",
        ),
    )

    orchestrator.start_run(integration_run)

    integration_plan = planner.create_plan(
        workflow_run_id=integration_run.run_id,
        decision="QUALIFY",
        decision_reason=(
            "Company matches the qualification criteria."
        ),
    )

    integration_action = integration_plan.actions[0]

    integration_run.results["action_plan"] = (
        integration_plan.model_dump()
    )

    integration_task = WorkflowTask(
        task_id=integration_action.action_id,
        name=integration_action.action_type.value,
        description=integration_action.description,
        risk_level=integration_action.risk_level,
        requires_human_approval=(
            integration_action.requires_human_approval
        ),
    )

    orchestrator.prepare_task(
        integration_run,
        integration_task,
    )

    print(
        f"Workflow status: "
        f"{integration_run.status}"
    )
    print(
        f"Current task: "
        f"{integration_run.current_task}"
    )
    print(
        f"Action type: "
        f"{integration_action.action_type}"
    )
    print(
        f"Action status: "
        f"{integration_action.status}"
    )
    print(
        f"Approval required: "
        f"{integration_action.requires_human_approval}"
    )

    assert (
        integration_run.status
        == WorkflowStatus.WAITING_FOR_APPROVAL
    )
    assert (
        integration_run.current_task
        == integration_action.action_id
    )
    assert (
        integration_run.results["action_plan"]["actions"][0][
            "action_type"
        ]
        == "CREATE_OUTREACH"
    )
    assert integration_run.approval_request is not None
    assert (
        integration_run.approval_request.status
        == ApprovalStatus.PENDING
    )

    print("PASS")

    # =========================================================
    # FINAL
    # =========================================================

    print("\n========================================")
    print("ALL ENGINE TESTS PASSED")
    print("========================================")


if __name__ == "__main__":
    main()