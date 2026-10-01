from typing import Literal

from pydantic import BaseModel, Field


class ResearchResult(BaseModel):
    company_name: str
    website: str
    location: str
    services: list[str]
    likely_customer_type: str
    relevant_business_information: list[str]
    possible_business_needs: list[str]
    assumptions: list[str]


class DataResult(BaseModel):
    company_name: str
    official_website: str | None = None
    location: str | None = None
    services: list[str] = Field(default_factory=list)
    customer_type: str | None = None
    business_information: list[str] = Field(
        default_factory=list
    )
    possible_business_needs: list[str] = Field(
        default_factory=list
    )
    missing_information: list[str] = Field(
        default_factory=list
    )
    conflicting_information: list[str] = Field(
        default_factory=list
    )
    assumptions: list[str] = Field(
        default_factory=list
    )


class VerificationResult(BaseModel):
    company_name: str
    verified_website: str | None = None
    verified_location: str | None = None
    verified_services: list[str] = Field(
        default_factory=list
    )
    verified_customer_type: str | None = None
    verified_business_information: list[str] = Field(
        default_factory=list
    )
    verified_business_needs: list[str] = Field(
        default_factory=list
    )
    unverified_information: list[str] = Field(
        default_factory=list
    )
    conflicting_information: list[str] = Field(
        default_factory=list
    )
    verification_notes: list[str] = Field(
        default_factory=list
    )


class AnalysisResult(BaseModel):
    business_signals: list[str]
    possible_needs: list[str]
    risks_or_missing_information: list[str]
    relevance_reason: str


class QualificationResult(BaseModel):
    qualification: Literal[
        "QUALIFIED",
        "NOT_QUALIFIED",
        "NEEDS_MORE_INFORMATION",
        "HUMAN_REVIEW",
    ]
    evidence: list[str] = Field(
        default_factory=list
    )
    missing_information: list[str] = Field(
        default_factory=list
    )
    risks: list[str] = Field(
        default_factory=list
    )
    reason: str


class DecisionResult(BaseModel):
    action: Literal[
        "QUALIFY",
        "REJECT",
        "NEED_MORE_INFORMATION",
        "HUMAN_REVIEW",
    ]
    reason: str