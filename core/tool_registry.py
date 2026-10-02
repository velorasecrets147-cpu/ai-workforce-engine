from core.tool_models import (
    ToolDefinition,
    ToolStatus,
)


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        tool: ToolDefinition,
    ) -> None:

        if tool.name in self._tools:
            raise ValueError(
                f"Tool '{tool.name}' is already registered."
            )

        self._tools[tool.name] = tool

    def get(
        self,
        tool_name: str,
    ) -> ToolDefinition:

        tool = self._tools.get(tool_name)

        if tool is None:
            raise ValueError(
                f"Tool '{tool_name}' is not registered."
            )

        if tool.status != ToolStatus.AVAILABLE:
            raise ValueError(
                f"Tool '{tool_name}' is not available."
            )

        return tool

    def list_tools(self) -> list[ToolDefinition]:
        return list(self._tools.values())

    def exists(
        self,
        tool_name: str,
    ) -> bool:

        return tool_name in self._tools