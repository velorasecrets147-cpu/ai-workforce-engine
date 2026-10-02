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
from core.tool_executor import ToolExecutor
from core.tool_models import (
    ToolDefinition,
    ToolResult,
    ToolStatus,
)
from core.tool_registry import ToolRegistry
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
    # TEST 11 — TOOL REGISTRY
    # =========================================================

    print("\n========================================")
    print("TEST 11 — TOOL REGISTRY")
    print("========================================")

    registry = ToolRegistry()

    email_tool = ToolDefinition(
        name="email",
        description="Send or prepare business email.",
    )

    registry.register(email_tool)

    registered_tool = registry.get("email")

    print(f"Tool name: {registered_tool.name}")
    print(f"Tool status: {registered_tool.status}")
    print(f"Tool exists: {registry.exists('email')}")

    assert registered_tool.name == "email"
    assert registered_tool.status == ToolStatus.AVAILABLE
    assert registry.exists("email") is True
    assert len(registry.list_tools()) == 1

    print("PASS")

    # =========================================================
    # TEST 12 — TOOL EXECUTOR
    # =========================================================

    print("\n========================================")
    print("TEST 12 — TOOL EXECUTOR")
    print("========================================")

    executor = ToolExecutor(registry)

    def email_handler(parameters: dict) -> ToolResult:

        recipient = parameters.get(
            "recipient",
            "unknown",
        )

        return ToolResult(
            success=True,
            tool_name="email",
            message="Email tool executed successfully.",
            data={
                "recipient": recipient,
                "mode": "simulated",
            },
        )

    executor.register_handler(
        "email",
        email_handler,
    )

    tool_result = executor.execute(
        "email",
        {
            "recipient": "demo@example.com",
        },
    )

    print(f"Success: {tool_result.success}")
    print(f"Tool: {tool_result.tool_name}")
    print(f"Message: {tool_result.message}")
    print(f"Data: {tool_result.data}")

    assert tool_result.success is True
    assert tool_result.tool_name == "email"
    assert (
        tool_result.message
        == "Email tool executed successfully."
    )
    assert (
        tool_result.data["recipient"]
        == "demo@example.com"
    )
    assert tool_result.data["mode"] == "simulated"

    print("PASS")

    # =========================================================
    # TEST 13 — MISSING TOOL HANDLER
    # =========================================================

    print("\n========================================")
    print("TEST 13 — MISSING TOOL HANDLER")
    print("========================================")

    registry_without_handler = ToolRegistry()

    browser_tool = ToolDefinition(
        name="browser",
        description="Interact with a web browser.",
    )

    registry_without_handler.register(browser_tool)

    executor_without_handler = ToolExecutor(
        registry_without_handler
    )

    missing_handler_result = executor_without_handler.execute(
        "browser"
    )

    print(
        f"Success: "
        f"{missing_handler_result.success}"
    )
    print(
        f"Tool: "
        f"{missing_handler_result.tool_name}"
    )
    print(
        f"Message: "
        f"{missing_handler_result.message}"
    )

    assert missing_handler_result.success is False
    assert missing_handler_result.tool_name == "browser"
    assert (
        "No execution handler"
        in missing_handler_result.message
    )

    print("PASS")

    # =========================================================
    # TEST 14 — TOOL FAILURE HANDLING
    # =========================================================

    print("\n========================================")
    print("TEST 14 — TOOL FAILURE HANDLING")
    print("========================================")

    failing_registry = ToolRegistry()

    failing_tool = ToolDefinition(
        name="failing_tool",
        description="Tool used to test execution failures.",
    )

    failing_registry.register(failing_tool)

    failing_executor = ToolExecutor(
        failing_registry
    )

    def failing_handler(parameters: dict) -> ToolResult:

        raise RuntimeError("Simulated tool failure.")

    failing_executor.register_handler(
        "failing_tool",
        failing_handler,
    )

    failure_result = failing_executor.execute(
        "failing_tool"
    )

    print(f"Success: {failure_result.success}")
    print(f"Tool: {failure_result.tool_name}")
    print(f"Message: {failure_result.message}")

    assert failure_result.success is False
    assert failure_result.tool_name == "failing_tool"
    assert (
        "Tool execution failed"
        in failure_result.message
    )

    print("PASS")

    # =========================================================
    # TEST 15 — HIGH RISK TOOL BLOCKED
    # =========================================================

    print("\n========================================")
    print("TEST 15 — HIGH RISK TOOL BLOCKED")
    print("========================================")

    protected_registry = ToolRegistry()

    protected_registry.register(
        ToolDefinition(
            name="email",
            description="Send business email.",
        )
    )

    protected_executor = ToolExecutor(
        protected_registry
    )

    protected_executor.register_handler(
        "email",
        email_handler,
    )

    high_risk_plan = planner.create_plan(
        workflow_run_id="run-protected-001",
        decision="QUALIFY",
        decision_reason=(
            "Company qualified for outreach."
        ),
    )

    protected_action = high_risk_plan.actions[0]

    blocked_result = protected_executor.execute(
        "email",
        {
            "recipient": "demo@example.com",
        },
        action=protected_action,
        approved=False,
    )

    print(f"Success: {blocked_result.success}")
    print(f"Tool: {blocked_result.tool_name}")
    print(f"Message: {blocked_result.message}")

    assert blocked_result.success is False
    assert blocked_result.tool_name == "email"
    assert (
        "blocked by permission policy"
        in blocked_result.message
    )

    print("PASS")

    # =========================================================
    # TEST 16 — HIGH RISK TOOL APPROVED
    # =========================================================

    print("\n========================================")
    print("TEST 16 — HIGH RISK TOOL APPROVED")
    print("========================================")

    approved_result = protected_executor.execute(
        "email",
        {
            "recipient": "demo@example.com",
        },
        action=protected_action,
        approved=True,
    )

    print(f"Success: {approved_result.success}")
    print(f"Tool: {approved_result.tool_name}")
    print(f"Message: {approved_result.message}")
    print(f"Data: {approved_result.data}")

    assert approved_result.success is True
    assert approved_result.tool_name == "email"
    assert (
        approved_result.data["recipient"]
        == "demo@example.com"
    )

    print("PASS")

    # =========================================================
    # TEST 17 — TOOL DOES NOT MATCH PLANNED ACTION
    # =========================================================

    print("\n========================================")
    print("TEST 17 — TOOL DOES NOT MATCH PLANNED ACTION")
    print("========================================")

    mismatch_result = protected_executor.execute(
        "email",
        {
            "recipient": "demo@example.com",
        },
        action=review_action,
        approved=True,
    )

    print(f"Success: {mismatch_result.success}")
    print(f"Tool: {mismatch_result.tool_name}")
    print(f"Message: {mismatch_result.message}")

    assert mismatch_result.success is False
    assert mismatch_result.tool_name == "email"
    assert (
        "does not match"
        in mismatch_result.message
    )

    print("PASS")

    # =========================================================
    # TEST 18 — REGISTERED EMAIL TOOL
    # =========================================================

    print("\n========================================")
    print("TEST 18 — REGISTERED EMAIL TOOL")
    print("========================================")

    from tools.register_tools import create_tool_executor

    application_executor = create_tool_executor()

    registered_email_result = application_executor.execute(
        "email",
        {
            "recipient": "client@example.com",
            "subject": "Business Partnership",
            "body": (
                "Hello, we would like to discuss "
                "a potential business partnership."
            ),
        },
    )

    print(
        f"Success: "
        f"{registered_email_result.success}"
    )
    print(
        f"Tool: "
        f"{registered_email_result.tool_name}"
    )
    print(
        f"Message: "
        f"{registered_email_result.message}"
    )
    print(
        f"Data: "
        f"{registered_email_result.data}"
    )

    assert registered_email_result.success is True
    assert registered_email_result.tool_name == "email"
    assert (
        registered_email_result.message
        == "Email prepared successfully."
    )
    assert (
        registered_email_result.data["recipient"]
        == "client@example.com"
    )
    assert (
        registered_email_result.data["subject"]
        == "Business Partnership"
    )
    assert (
        registered_email_result.data["sent"]
        is False
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