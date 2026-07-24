import json
import os

from dotenv import load_dotenv
from groq import Groq
from pydantic import ValidationError
from tenacity import retry, stop_after_attempt, retry_if_exception_type

from schema import AgentStep, ALLOWED_TOOLS
from tools import TOOL_FUNCTIONS

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "shared_inputs.json")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "openai/gpt-oss-120b"

# ----------------------------------------------------------------------
# THE TWO CONSTRAINTS THAT MAKE THIS AGENT "CONSTRAINED"
# (kept at module level, on purpose -- easy to find, not buried)
# ----------------------------------------------------------------------
MAX_STEPS = 6
# ALLOWED_TOOLS is imported from schema.py and enforced by AgentStep's
# Literal type -- the model literally cannot request a tool outside it.

SYSTEM_PROMPT = f"""You are a hotel front-desk triage agent. A guest has
reported an issue. Decide whether to dispatch a technician, reassign the
guest to a new room, or escalate to a human manager.

You reason step by step. On EACH turn, respond with ONLY a JSON object,
no other text, matching this exact shape:
{{"thought": "<your reasoning>", "tool": "<one tool name>", "tool_input": {{...}}}}

Allowed tool names, exactly as written: {ALLOWED_TOOLS}

Guidance:
- Check guest history before deciding severity (VIP status and recent
  issue count both matter).
- Only check room availability if you are actually considering
  reassignment.
- You MUST end every run in either "final_answer" (tool_input should
  contain "summary" and "action_taken") or "escalate_to_manager"
  (tool_input should contain "reason"). No other stopping point is valid.
- If you are not confident, escalate_to_manager rather than guessing.
"""


class StepValidationError(Exception):
    pass


@retry(stop=stop_after_attempt(3), retry=retry_if_exception_type(StepValidationError))
def get_valid_step(messages: list) -> tuple[AgentStep, list]:
    """
    Calls the model and validates its response against AgentStep.
    On failure, appends a corrective message and raises so tenacity retries
    (bounded to 3 attempts total -- this is the "bounded-retry" logic
    tenacity is for; it does not loop forever on a stubborn model).
    """
    response = client.chat.completions.create(
        messages=messages,
        model=MODEL_NAME,
        temperature=0.0,
    )
    raw = response.choices[0].message.content.strip()

    try:
        parsed = json.loads(raw)
        step = AgentStep(**parsed)
    except (json.JSONDecodeError, ValidationError) as e:
        messages.append({"role": "assistant", "content": raw})
        messages.append({
            "role": "user",
            "content": f"That response failed schema validation ({e}). "
                       f"Reply again with ONLY valid JSON matching the required shape.",
        })
        raise StepValidationError(str(e))

    return step, messages


def run_agent(guest_data: dict) -> dict:
    phone = guest_data.get("phone_number", "")
    message = guest_data.get("message", "")

    print(f"\n[Phone {phone}] reported: '{message}'")

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Guest phone: {phone}\nGuest message: {message}"},
    ]

    for step_num in range(1, MAX_STEPS + 1):
        try:
            step, messages = get_valid_step(messages)
        except StepValidationError:
            print(f"  -> Step {step_num}: model failed to produce a valid step after 3 retries.")
            print("  -> FORCED EXIT: escalate_to_manager (validation budget exhausted).")
            return {"status": "escalated", "reason": "schema_validation_failed"}

        print(f"  -> Step {step_num} | thought: {step.thought}")
        print(f"     tool: {step.tool} | input: {step.tool_input}")

        if step.tool == "final_answer":
            print(f"  -> FINAL ANSWER: {step.tool_input}")
            return {"status": "final_answer", **step.tool_input}

        if step.tool == "escalate_to_manager":
            print(f"  -> ESCALATED: {step.tool_input}")
            return {"status": "escalated", **step.tool_input}

        # Execute the allow-listed tool and feed the observation back in.
        tool_fn = TOOL_FUNCTIONS[step.tool]
        observation = tool_fn(**step.tool_input)
        print(f"     observation: {observation}")

        messages.append({"role": "assistant", "content": step.model_dump_json()})
        messages.append({"role": "user", "content": f"Observation: {json.dumps(observation)}"})

    # MAX_STEPS budget exhausted without a final_answer/escalate -- never
    # let the loop just silently stop, force a safe exit.
    print(f"  -> MAX_STEPS ({MAX_STEPS}) reached without a final answer.")
    print("  -> FORCED EXIT: escalate_to_manager (step budget exhausted).")
    return {"status": "escalated", "reason": "max_steps_exhausted"}


def load_inputs():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Could not find {INPUT_FILE}.")
    with open(INPUT_FILE, "r") as file:
        return json.load(file)


def main():
    print("=== Starting Constrained ReAct Agent ===")
    try:
        inputs = load_inputs()
        for guest_request in inputs:
            run_agent(guest_request)
    except Exception as e:
        print(f"Error initializing agent: {e}")

    print("\n=== Agent Execution Finished ===")


if __name__ == "__main__":
    main()
