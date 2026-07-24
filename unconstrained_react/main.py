import json
import os
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def maintenance(issue: str) -> str:
    return f"SUCCESS: Maintenance team dispatched for issue: '{issue}'."

def hvac(issue: str) -> str:
    return f"SUCCESS: HVAC technician dispatched for issue: '{issue}'."

def security(issue: str) -> str:
    return f"SUCCESS: Security dispatched for issue: '{issue}'."

def escalate_to_manager(issue: str) -> str:
    return f"SUCCESS: Issue escalated to Front Desk Manager: '{issue}'."

AVAILABLE_TOOLS = {
    "dispatch_maintenance": maintenance,
    "dispatch_hvac": hvac,
    "dispatch_security": security,
    "escalate_to_manager": escalate_to_manager
}

PROMPT = """
You are an AI Concierge Agent for Aurelia Hotels. Your job is to resolve guest issues by reasoning step-by-step and using available tools.
You MUST follow this exact format for each step:
Thought: Describe your step-by-step reasoning about what the issue is and what to do next.
Action: The name of the tool to call. Must be strictly ONE of: dispatch_maintenance, dispatch_hvac, dispatch_security, escalate_to_manager.
Action Input: The details or issue description for the tool.
Observation: [System will execute the action and return the result here]
You can repeat Thought/Action/Action Input/Observation as many times as you need until you have resolved the issue.
When you are done and have solved the issue, output:
Final Answer: A clear, polite resolution message to the guest explaining what action was taken.
Begin!
"""
def run_unconstrained_react(user_issue: str):
    messages = [
        {"role": "system", "content": PROMPT},
        {"role": "user", "content": f"Guest Issue: '{user_issue}'"}
    ]
    total_tokens = 0
    start_time = time.time()
    step_count = 0

    while True:
        step_count += 1
        
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,
            stop=["Observation:"]
        )
        
        if response.usage:
            total_tokens += response.usage.total_tokens
            
        ai_response = response.choices[0].message.content.strip()
        print(f"\n--- [Step {step_count}] AI Output ---")
        print(ai_response)
        
        messages.append({"role": "assistant", "content": ai_response})
        
        if "Final Answer:" in ai_response:
            execution_time = round(time.time() - start_time, 2)
            return {
                "response": ai_response.split("Final Answer:")[-1].strip(),
                "steps": step_count,
                "tokens": total_tokens,
                "time_sec": execution_time
            }
            
        if "Action:" in ai_response and "Action Input:" in ai_response:
            try:
                lines = ai_response.split("\n")
                tool_name = ""
                tool_input = ""
                
                for line in lines:
                    if line.startswith("Action:"):
                        tool_name = line.replace("Action:", "").strip()
                    elif line.startswith("Action Input:"):
                        tool_input = line.replace("Action Input:", "").strip()
                
                if tool_name in AVAILABLE_TOOLS:
                    observation = AVAILABLE_TOOLS[tool_name](tool_input)
                else:
                    observation = f"ERROR: Tool '{tool_name}' is not available."
            except Exception as e:
                observation = f"ERROR: Failed to parse action or input ({str(e)})"
                
            print(f"-> [System Observation]: {observation}")
            
            messages.append({"role": "user", "content": f"Observation: {observation}"})
        else:
            messages.append({"role": "user", "content": "Please continue using Thought/Action/Observation or provide Final Answer."})
def main():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    json_path = os.path.join(BASE_DIR, "shared_inputs.json")
    
    with open(json_path, "r", encoding="utf-8") as f:
        cases = json.load(f)
        
    print("Starting Unconstrained ReAct Agent")
    
    for idx, case in enumerate(cases, 1):
        issue_text = case.get('message')
        
        print(f"RUNNING CASE {idx}: Phone {case.get('phone_number')}")
        print(f"Reported Issue: '{issue_text}'")
        
        result = run_unconstrained_react(issue_text)
        
        print("\n CASE RESULT : ")
        print(f"Final Answer  : {result['response']}")
        print(f"Steps Taken   : {result['steps']}")
        print(f"Total Tokens  : {result['tokens']}")
        print(f"Execution Time: {result['time_sec']} seconds")


if __name__ == "__main__":
    main()