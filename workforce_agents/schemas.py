from typing import Literal

from pydantic import BaseModel


class ResearchResult(BaseModel):
    company_name: str
    website: str
    location: str
    services: list[str]
    likely_customer_type: str
    relevant_business_information: list[str]
    possible_business_needs: list[str]
    assumptions: list[str]


class AnalysisResult(BaseModel):
    business_signals: list[str]
    possible_needs: list[str]
    risks_or_missing_information: list[str]
    relevance_reason: str


class DecisionResult(BaseModel):
    action: Literal[
        "QUALIFY",
        "REJECT",
        "NEED_MORE_INFORMATION",
        "HUMAN_REVIEW",
    ]
    reason: str