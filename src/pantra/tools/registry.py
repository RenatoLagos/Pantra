from __future__ import annotations

from pantra.tools.base import Tool
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

REGISTRY: dict[str, Tool] = {
    t.name: t() for t in (
        ListServicesTool,
        ListPractitionersTool,
        SearchKnowledgeTool,
        GetTreatmentDetailsTool,
        CheckAvailabilityTool,
        CreateBookingTool,
        RescheduleBookingTool,
        CancelBookingTool,
        CreateLeadTool,
        HandoffToHumanTool,
    )
}


def get_tool(name: str) -> Tool:
    try:
        return REGISTRY[name]
    except KeyError as e:
        raise ValueError(f"unknown tool: {name!r}") from e
