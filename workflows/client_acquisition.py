import uuid

from agents import Runner

from core.models import (
    BusinessContext,
    RiskLevel,
    WorkflowTask,
)
from core.orchestrator import WorkflowOrchestrator
from evaluation.evaluator import WorkflowEvaluator
from workforce_agents.analysis_agent import analysis_agent
from workforce_agents.decision_agent import decision_agent
from workforce_agents.research_agent import research_agent


async def run_client_acquisition(
    company_name: str,
    business_name: str = "AI Workforce Engine",
):
    orchestrator = WorkflowOrchestrator()
    evaluator = WorkflowEvaluator()

    # ----------------------------------------
    # BUSINESS CONTEXT
    # ----------------------------------------

    business_context = BusinessContext(
        business_name=business_name,
        business_type="B2B Service",
        process_name="Client Acquisition",
        goals=[
            "Find qualified companies",
            "Identify business needs",
            "Recommend the next workflow action",
        ],
        constraints=[
            "Do not contact companies without approval",
            "Do not invent company information",
        ],
    )

    # ----------------------------------------
    # CREATE WORKFLOW RUN
    # ----------------------------------------

    workflow_run = orchestrator.create_run(
        run_id=str(uuid.uuid4()),
        workflow_name="client_acquisition",
        business_context=business_context,
    )

    orchestrator.start_run(workflow_run)

    # ----------------------------------------
    # STEP 1 — RESEARCH
    # ----------------------------------------

    research_task = WorkflowTask(
        task_id="research",
        name="Research Company",
        description=(
            "Research and structure verified "
            "company information."
        ),
        risk_level=RiskLevel.LOW,
    )

    orchestrator.prepare_task(
        workflow_run,
        research_task,
    )

    research_result = await Runner.run(
        research_agent,
        f"""
Research this target company:

{company_name}

Return structured research according to
your defined output schema.
""",
    )

    research_data = research_result.final_output

    # ----------------------------------------
    # STEP 2 — ANALYSIS
    # ----------------------------------------

    analysis_task = WorkflowTask(
        task_id="analysis",
        name="Analyze Company",
        description=(
            "Analyze research and identify "
            "business signals and possible needs."
        ),
        risk_level=RiskLevel.LOW,
    )

    orchestrator.prepare_task(
        workflow_run,
        analysis_task,
    )

    analysis_result = await Runner.run(
        analysis_agent,
        f"""
Analyze the following structured research:

{research_data.model_dump_json(indent=2)}

Identify business signals, possible needs,
risks, missing information, and relevance.
""",
    )

    analysis_data = analysis_result.final_output

    # ----------------------------------------
    # STEP 3 — DECISION
    # ----------------------------------------

    decision_task = WorkflowTask(
        task_id="decision",
        name="Make Qualification Decision",
        description=(
            "Determine the next workflow action "
            "based on research and analysis."
        ),
        risk_level=RiskLevel.MEDIUM,
    )

    orchestrator.prepare_task(
        workflow_run,
        decision_task,
    )

    decision_result = await Runner.run(
        decision_agent,
        f"""
Research:

{research_data.model_dump_json(indent=2)}

Analysis:

{analysis_data.model_dump_json(indent=2)}

Determine the next workflow action using
only the supplied evidence.
""",
    )

    decision_data = decision_result.final_output

    # ----------------------------------------
    # STORE WORKFLOW RESULTS
    # ----------------------------------------

    workflow_run.results.update(
        {
            "research": research_data.model_dump(),
            "analysis": analysis_data.model_dump(),
            "decision": decision_data.model_dump(),
        }
    )

    # ----------------------------------------
    # STEP 4 — OUTREACH
    # ----------------------------------------
    #
    # Outreach is HIGH RISK.
    # Therefore human approval is required.
    #

    outreach_task = WorkflowTask(
        task_id="outreach",
        name="Client Outreach",
        description=(
            "Contact the qualified company "
            "after human approval."
        ),
        risk_level=RiskLevel.HIGH,
        requires_human_approval=True,
    )

    orchestrator.prepare_task(
        workflow_run,
        outreach_task,
    )

    # ----------------------------------------
    # HUMAN APPROVAL REQUIRED
    # ----------------------------------------

    if (
        workflow_run.status.value
        == "WAITING_FOR_APPROVAL"
    ):
        return {
            "workflow_run": workflow_run,
            "research": research_data,
            "analysis": analysis_data,
            "decision": decision_data,
            "evaluation": None,
        }

    # ----------------------------------------
    # EVALUATION
    # ----------------------------------------

    evaluation = evaluator.evaluate(
        task_completed=True,
        output_quality=1.0,
        business_outcome=decision_data.action,
    )

    workflow_run.results["evaluation"] = (
        evaluation.model_dump()
    )

    # ----------------------------------------
    # FINAL RESULT
    # ----------------------------------------

    return {
        "workflow_run": workflow_run,
        "research": research_data,
        "analysis": analysis_data,
        "decision": decision_data,
        "evaluation": evaluation,
    }