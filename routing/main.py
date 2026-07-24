import json
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FILE = os.path.join(BASE_DIR, 'shared_inputs.json')
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def load_inputs():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Could not find {INPUT_FILE}.")
    with open(INPUT_FILE, 'r') as file:
        return json.load(file)

def classify_issue_with_llm(issue_text):
    prompt = f"""
    You are an automated hotel triage system.
    Read the guest's issue and classify it strictly into ONE of the following categories:
    - WATER_DAMAGE
    - HVAC_FAILURE
    - ACCESS_ISSUE
    - HAZARD_UNKNOWN

    Guest Issue: "{issue_text}"

    Respond with ONLY the exact category name and absolutely nothing else.
    """
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a precise classification router."},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during API call: {e}")
        return "HAZARD_UNKNOWN"

def route_and_execute(category, guest_data):
    if category == "WATER_DAMAGE":
        print(f"  -> ROUTED TO: Water Damage Protocol")
        print("  -> ACTION: Dispatching maintenance to fix the leak.")
        print("  -> LIMITATION: Cannot check VIP status or room without tools. Cannot reassign!")

    elif category == "HVAC_FAILURE":
        print(f"  -> ROUTED TO: HVAC Protocol")
        print("  -> ACTION: Dispatching HVAC technician.")

    elif category == "ACCESS_ISSUE":
        print(f"  -> ROUTED TO: Access Protocol")
        print("  -> ACTION: Dispatching Security to investigate.")
        
    elif category == "HAZARD_UNKNOWN":
        print(f"  -> ROUTED TO: Fallback Protocol")
        print("  -> ACTION: Escalating to human Front Desk Manager to investigate.")
        
    else:
        print(f"  -> ROUTED TO: Unrecognized Category ({category})")
        print("  -> ACTION: Failsafe triggered. Escalating to human.")

def main():
    print("=== Starting Deterministic Routing Agent ===")
    try:
        inputs = load_inputs()
        for guest_request in inputs:
            issue = guest_request.get("message", "")
            phone = guest_request.get("phone_number", "")
            
            print(f"\n[Phone {phone}] reported: '{issue}'")
            
            category = classify_issue_with_llm(issue)
            print(f"  -> LLM CLASSIFICATION: {category}")
            
            route_and_execute(category, guest_request)
            
    except Exception as e:
        print(f"Error initializing agent: {e}")
        
    print("\n=== Agent Execution Finished ===")

if __name__ == "__main__":
    main()