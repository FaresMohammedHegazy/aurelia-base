import json
import os

from dotenv import load_dotenv
from groq import Groq

from schema import AgentStep
from tools import *

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "shared_inputs.json"
)


MAX_STEPS = 6

ALLOWED_TOOLS = {

    "dispatch_maintenance": dispatch_maintenance,

    "dispatch_hvac": dispatch_hvac,

    "dispatch_security": dispatch_security,

    "escalate_manager": escalate_manager
}

SYSTEM_PROMPT = """
You are a constrained hotel complaint agent.

Rules:

1. Think step by step.

2. You may ONLY use one of these actions:

- dispatch_maintenance
- dispatch_hvac
- dispatch_security
- escalate_manager
- final_answer

3. Return ONLY JSON.

Schema:

{
"thought":"",
"action":"",
"action_input":""
}

Never write normal text.

If the problem is solved return:

{
"thought":"",
"action":"final_answer",
"action_input":"resolved"
}
"""
