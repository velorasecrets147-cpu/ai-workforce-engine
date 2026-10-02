from collections.abc import Callable

from core.models import RiskLevel
from core.planning import PlannedAction
from core.permissions import PermissionManager
from core.tool_models import ToolResult
from core.tool_registry import ToolRegistry


class ToolExecutor:

    def __init__(
        self,
        registry: ToolRegistry,
        permission_manager: PermissionManager | None = None,
    ):
        self.registry = registry
        self.permission_manager = (
            permission_manager
            or PermissionManager()
        )
        self._handlers: dict[
            str,
            Callable[[dict], ToolResult],
        ] = {}

    def register_handler(
        self,
        tool_name: str,
        handler: Callable[[dict], ToolResult],
    ) -> None:

        self.registry.get(tool_name)

        if tool_name in self._handlers:
            raise ValueError(
                f"Handler for tool '{tool_name}' "
                "is already registered."
            )

        self._handlers[tool_name] = handler

    def execute(
        self,
        tool_name: str,
        parameters: dict | None = None,
        action: PlannedAction | None = None,
        approved: bool = False,
    ) -> ToolResult:

        parameters = parameters or {}

        try:
            tool = self.registry.get(tool_name)
        except ValueError as exc:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                message=str(exc),
            )

        if action is not None:

            if action.tool_name != tool_name:
                return ToolResult(
                    success=False,
                    tool_name=tool_name,
                    message=(
                        "Tool does not match "
                        "the planned action."
                    ),
                )

            if not self.permission_manager.can_execute_tool(
                action,
                approved=approved,
            ):
                return ToolResult(
                    success=False,
                    tool_name=tool_name,
                    message=(
                        "Tool execution blocked by "
                        "permission policy."
                    ),
                )

        handler = self._handlers.get(tool.name)

        if handler is None:
            return ToolResult(
                success=False,
                tool_name=tool.name,
                message=(
                    f"No execution handler is registered "
                    f"for tool '{tool.name}'."
                ),
            )

        try:
            result = handler(parameters)

            if not isinstance(result, ToolResult):
                raise TypeError(
                    "Tool handler must return ToolResult."
                )

            return result

        except Exception as exc:
            return ToolResult(
                success=False,
                tool_name=tool.name,
                message=f"Tool execution failed: {exc}",
            )