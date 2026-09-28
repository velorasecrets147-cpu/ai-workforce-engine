from agents import Runner

from workforce_agents.research_agent import research_agent
from workforce_agents.analysis_agent import analysis_agent
from workforce_agents.decision_agent import decision_agent


async def run_client_acquisition(company_name: str):

    # Step 1: Research
    research_result = await Runner.run(
        research_agent,
        f"Research this company: {company_name}"
    )

    research_data = research_result.final_output.model_dump_json(indent=2)

    # Step 2: Analysis
    analysis_result = await Runner.run(
        analysis_agent,
        f"""
Analyze the following structured research:

{research_data}
"""
    )

    analysis_data = analysis_result.final_output.model_dump_json(indent=2)

    # Step 3: Decision
    decision_result = await Runner.run(
        decision_agent,
        f"""
Review the following research and analysis.

RESEARCH:
{research_data}

ANALYSIS:
{analysis_data}

Determine the next workflow action.
"""
    )

    return {
        "research": research_result.final_output,
        "analysis": analysis_result.final_output,
        "decision": decision_result.final_output,
    }