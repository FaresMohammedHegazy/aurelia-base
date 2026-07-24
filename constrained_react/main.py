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
