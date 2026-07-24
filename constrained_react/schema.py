

from typing import Literal
from pydantic import BaseModel, Field


ALLOWED_TOOLS = [
    "check_guest_history",     # look up VIP status + recent complaint count
    "check_room_availability", # list rooms free for reassignment
    "dispatch_technician",     # send maintenance/HVAC/security
    "reassign_guest",          # move guest to a new room
    "escalate_to_manager",     # hand off to a human, always a safe exit
    "final_answer",            # the only other valid way to stop
]


class AgentStep(BaseModel):
    """
    One turn of the ReAct loop. The model must return JSON matching this
    shape exactly, or the step is rejected and retried.
    """
    thought: str = Field(..., min_length=1, description="Brief reasoning for this step")
    tool: Literal[
        "check_guest_history",
        "check_room_availability",
        "dispatch_technician",
        "reassign_guest",
        "escalate_to_manager",
        "final_answer",
    ]
    tool_input: dict = Field(default_factory=dict)
