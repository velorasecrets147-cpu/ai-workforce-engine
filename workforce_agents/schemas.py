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


class DataResult(BaseModel):

    company_name: str

    website: str

    location: str

    services: list[str]

    likely_customer_type: str

    relevant_business_information: list[str]

    possible_business_needs: list[str]

    missing_information: list[str]

    conflicting_information: list[str]

    assumptions: list[str]


class VerificationResult(BaseModel):

    company_name: str

    website: str

    verified_fields: list[str]

    unverified_fields: list[str]

    conflicting_information: list[str]

    missing_information: list[str]

    verification_notes: list[str]


class QualificationResult(BaseModel):

    status: Literal[
        "QUALIFIED",
        "NOT_QUALIFIED",
        "NEEDS_MORE_INFORMATION",
        "HUMAN_REVIEW",
    ]

    reason: str

    supporting_evidence: list[str]

    missing_information: list[str]

    risks: list[str]