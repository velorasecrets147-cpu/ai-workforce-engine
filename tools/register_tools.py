from core.tool_executor import ToolExecutor
from core.tool_models import ToolDefinition
from core.tool_registry import ToolRegistry
from tools.email_tool import prepare_email


def create_tool_executor() -> ToolExecutor:
    """
    Create the application's tool registry and executor.

    Tools are registered here so the workflow engine
    can use them through a controlled interface.
    """

    registry = ToolRegistry()

    registry.register(
        ToolDefinition(
            name="email",
            description=(
                "Prepare a business email without "
                "automatically sending it."
            ),
        )
    )

    executor = ToolExecutor(registry)

    executor.register_handler(
        "email",
        prepare_email,
    )

    return executor