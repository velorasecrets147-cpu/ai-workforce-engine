from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    task_completed: bool
    output_quality: float = Field(ge=0.0, le=1.0)
    business_outcome: str
    issues: list[str] = Field(default_factory=list)
    improvement_suggestions: list[str] = Field(default_factory=list)


class WorkflowEvaluator:

    def evaluate(
        self,
        task_completed: bool,
        output_quality: float,
        business_outcome: str,
        issues: list[str] | None = None,
    ) -> EvaluationResult:

        issues = issues or []
        suggestions = []

        if not task_completed:
            suggestions.append(
                "Investigate why the workflow task failed."
            )

        if output_quality < 0.7:
            suggestions.append(
                "Review instructions, tools, input quality, and agent output."
            )

        if not business_outcome:
            suggestions.append(
                "Define and capture a measurable business outcome."
            )

        return EvaluationResult(
            task_completed=task_completed,
            output_quality=output_quality,
            business_outcome=business_outcome,
            issues=issues,
            improvement_suggestions=suggestions,
        )