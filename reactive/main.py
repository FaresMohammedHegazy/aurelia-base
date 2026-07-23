import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FILE = os.path.join(BASE_DIR, 'shared_inputs.json')

def load_inputs():
    if not os.path.exists(INPUT_FILE):
        raise FileNotFoundError(f"Could not find {INPUT_FILE}.")
    with open(INPUT_FILE, 'r') as file:
        return json.load(file)

def reactive_room_reassignment_agent(guest_data):
    issue = guest_data.get("message", "").lower()
    phone = guest_data.get("phone_number", "")
    
    print(f"\n[Phone {phone}] reported: '{issue}'")
    
    # ---------------------------------------------------------
    # RULE 1: Severe Water Damage (Leak/Soaked)
    # ---------------------------------------------------------
    if "leak" in issue or "soaked" in issue:
        print("  -> CONDITION MET: Water damage detected.")
        print("  -> ACTION: Dispatching maintenance to fix the leak.")

    # ---------------------------------------------------------
    # RULE 2: HVAC Issues (Air Conditioning/Hot)
    # ---------------------------------------------------------
    elif "air conditioning" in issue or "hot" in issue:
        print("  -> CONDITION MET: HVAC failure detected.")
        print("  -> ACTION: Dispatching HVAC technician.")

    # ---------------------------------------------------------
    # RULE 3: Access Issues (Lock/Unresponsive)
    # ---------------------------------------------------------
    elif "lock" in issue or "unresponsive" in issue:
        print("  -> CONDITION MET: Door lock failure detected.")
        print("  -> ACTION: Dispatching Security to investigate.")
        
    # ---------------------------------------------------------
    # FALLBACK RULE: Unrecognized Issues
    # ---------------------------------------------------------
    else:
        print("  -> CONDITION MET: Unknown issue keywords.")
        print("  -> ACTION: Escalating to human Front Desk Manager.")

def main():
    print("=== Starting Reactive (Rule-Based) Agent ===")
    try:
        inputs = load_inputs()
        for guest_request in inputs:
            reactive_room_reassignment_agent(guest_request)
            
    except Exception as e:
        print(f"Error initializing agent: {e}")
        
    print("\n=== Agent Execution Finished ===")

if __name__ == "__main__":
    main()