from agents import Runner

from workforce_agents.research_agent import research_agent
from workforce_agents.analysis_agent import analysis_agent
from workforce_agents.decision_agent import decision_agent


async def run_client_acquisition(company_name: str):
    research_result = await Runner.run(
        research_agent,
        f"Research this company: {company_name}"
    )

    analysis_result = await Runner.run(
        analysis_agent,
        f"""
Analyze the following research:

{research_result.final_output}
"""
    )

    decision_result = await Runner.run(
        decision_agent,
        f"""
Research:
{research_result.final_output}

Analysis:
{analysis_result.final_output}
"""
    )

    return {
        "research": research_result.final_output,
        "analysis": analysis_result.final_output,
        "decision": decision_result.final_output,
    }