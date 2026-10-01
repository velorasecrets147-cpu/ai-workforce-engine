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
from workforce_agents.data_agent import data_agent
from workforce_agents.decision_agent import decision_agent
from workforce_agents.qualification_agent import qualification_agent
from workforce_agents.research_agent import research_agent
from workforce_agents.verification_agent import verification_agent


async def run_client_acquisition(
    company_name: str,
    business_name: str = "AI Workforce Engine",
):
    orchestrator = WorkflowOrchestrator()
    evaluator = WorkflowEvaluator()

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

    workflow_run = orchestrator.create_run(
        run_id=str(uuid.uuid4()),
        workflow_name="client_acquisition",
        business_context=business_context,
    )

    orchestrator.start_run(workflow_run)

    # =====================================================
    # STEP 1 — RESEARCH
    # =====================================================

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

    # =====================================================
    # STEP 2 — DATA
    # =====================================================

    data_task = WorkflowTask(
        task_id="data",
        name="Structure Business Data",
        description=(
            "Clean, normalize, and structure "
            "the research data."
        ),
        risk_level=RiskLevel.LOW,
    )

    orchestrator.prepare_task(
        workflow_run,
        data_task,
    )

    data_result = await Runner.run(
        data_agent,
        f"""
Convert the following research into clean,
structured business data.

Research:

{research_data.model_dump_json(indent=2)}

Do not invent missing information.
Identify missing and conflicting information.
""",
    )

    data = data_result.final_output

    # =====================================================
    # STEP 3 — VERIFICATION
    # =====================================================

    verification_task = WorkflowTask(
        task_id="verification",
        name="Verify Business Information",
        description=(
            "Verify important company information "
            "using reliable external sources."
        ),
        risk_level=RiskLevel.LOW,
    )

    orchestrator.prepare_task(
        workflow_run,
        verification_task,
    )

    verification_result = await Runner.run(
        verification_agent,
        f"""
Verify the following structured business data:

{data.model_dump_json(indent=2)}

Use reliable external sources when verification
is required.

Clearly separate verified information,
unverified information, conflicts, and notes.
""",
    )

    verification = verification_result.final_output

    # =====================================================
    # STEP 4 — ANALYSIS
    # =====================================================

    analysis_task = WorkflowTask(
        task_id="analysis",
        name="Analyze Company",
        description=(
            "Analyze verified business information "
            "and identify useful business signals."
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
Analyze the following business information.

STRUCTURED DATA:

{data.model_dump_json(indent=2)}

VERIFICATION:

{verification.model_dump_json(indent=2)}

Identify:

- business signals
- possible business needs
- risks or missing information
- relevance to the business

Use only the supplied evidence.
""",
    )

    analysis = analysis_result.final_output

    # =====================================================
    # STEP 5 — QUALIFICATION
    # =====================================================

    qualification_task = WorkflowTask(
        task_id="qualification",
        name="Qualify Company",
        description=(
            "Determine whether the company "
            "matches the qualification criteria."
        ),
        risk_level=RiskLevel.MEDIUM,
    )

    orchestrator.prepare_task(
        workflow_run,
        qualification_task,
    )

    qualification_result = await Runner.run(
        qualification_agent,
        f"""
Determine whether this company qualifies.

STRUCTURED DATA:

{data.model_dump_json(indent=2)}

VERIFICATION:

{verification.model_dump_json(indent=2)}

ANALYSIS:

{analysis.model_dump_json(indent=2)}

Use only the supplied evidence.

Allowed statuses:

QUALIFIED
NOT_QUALIFIED
NEEDS_MORE_INFORMATION
HUMAN_REVIEW
""",
    )

    qualification = qualification_result.final_output

    # =====================================================
    # STEP 6 — DECISION
    # =====================================================

    decision_task = WorkflowTask(
        task_id="decision",
        name="Make Workflow Decision",
        description=(
            "Determine the next workflow action "
            "based on qualification and analysis."
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
Determine the next workflow action.

QUALIFICATION:

{qualification.model_dump_json(indent=2)}

ANALYSIS:

{analysis.model_dump_json(indent=2)}

VERIFICATION:

{verification.model_dump_json(indent=2)}

Use only the supplied evidence.

Allowed actions:

QUALIFY
REJECT
NEED_MORE_INFORMATION
HUMAN_REVIEW
""",
    )

    decision = decision_result.final_output

    # =====================================================
    # STORE WORKFLOW RESULTS
    # =====================================================

    workflow_run.results.update(
        {
            "research": research_data.model_dump(),
            "data": data.model_dump(),
            "verification": verification.model_dump(),
            "analysis": analysis.model_dump(),
            "qualification": qualification.model_dump(),
            "decision": decision.model_dump(),
        }
    )

    # =====================================================
    # STEP 7 — HUMAN APPROVAL FOR OUTREACH
    # =====================================================

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

    if workflow_run.status.value == "WAITING_FOR_APPROVAL":
        return {
            "workflow_run": workflow_run,
            "research": research_data,
            "data": data,
            "verification": verification,
            "analysis": analysis,
            "qualification": qualification,
            "decision": decision,
            "evaluation": None,
        }

    # =====================================================
    # EVALUATION
    # =====================================================

    evaluation = evaluator.evaluate(
        task_completed=True,
        output_quality=1.0,
        business_outcome=decision.action,
    )

    workflow_run.results["evaluation"] = (
        evaluation.model_dump()
    )

    return {
        "workflow_run": workflow_run,
        "research": research_data,
        "data": data,
        "verification": verification,
        "analysis": analysis,
        "qualification": qualification,
        "decision": decision,
        "evaluation": evaluation,
    }