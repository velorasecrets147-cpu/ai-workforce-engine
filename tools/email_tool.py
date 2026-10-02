from core.tool_models import ToolResult


def prepare_email(parameters: dict) -> ToolResult:
    """
    Prepare an email without sending it.

    This is a deterministic tool:
    - no LLM
    - no external API
    - no network request
    - no automatic sending
    """

    recipient = parameters.get("recipient")
    subject = parameters.get("subject")
    body = parameters.get("body")

    if not recipient:
        return ToolResult(
            success=False,
            tool_name="email",
            message="Recipient is required.",
        )

    if not subject:
        return ToolResult(
            success=False,
            tool_name="email",
            message="Subject is required.",
        )

    if not body:
        return ToolResult(
            success=False,
            tool_name="email",
            message="Email body is required.",
        )

    return ToolResult(
        success=True,
        tool_name="email",
        message="Email prepared successfully.",
        data={
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "mode": "prepared_only",
            "sent": False,
        },
    )