from pydantic import BaseModel
from typing import Literal


class AgentStep(BaseModel):
    thought: str

    action: Literal[
        "dispatch_maintenance",
        "dispatch_hvac",
        "dispatch_security",
        "escalate_manager",
        "final_answer"
    ]

    action_input: str


class FinalAnswer(BaseModel):
    status: Literal["resolved", "escalated"]

    response: str
