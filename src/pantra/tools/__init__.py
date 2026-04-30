"""Actions the LLM can call. The ONLY layer that mutates business state."""
from pantra.tools.base import Tool, ToolContext, ToolError, anthropic_tool_definitions
from pantra.tools.booking import (
    CancelBookingTool,
    CheckAvailabilityTool,
    CreateBookingTool,
    RescheduleBookingTool,
)
from pantra.tools.catalog import ListPractitionersTool, ListServicesTool
from pantra.tools.handoff import HandoffToHumanTool
from pantra.tools.knowledge import GetTreatmentDetailsTool, SearchKnowledgeTool
from pantra.tools.lead import CreateLeadTool
from pantra.tools.registry import REGISTRY, get_tool

__all__ = [
    "REGISTRY",
    "CancelBookingTool",
    "CheckAvailabilityTool",
    "CreateBookingTool",
    "CreateLeadTool",
    "GetTreatmentDetailsTool",
    "HandoffToHumanTool",
    "ListPractitionersTool",
    "ListServicesTool",
    "SearchKnowledgeTool",
    "RescheduleBookingTool",
    "Tool",
    "ToolContext",
    "ToolError",
    "anthropic_tool_definitions",
    "get_tool",
]
