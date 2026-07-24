
GUEST_DB = {
    "555-0502": {"vip": False, "recent_issues": 1},
    "555-0210": {"vip": True, "recent_issues": 3},
    "555-0405": {"vip": False, "recent_issues": 0},
    "555-0112": {"vip": False, "recent_issues": 0},
}

ROOM_INVENTORY = {"available_rooms": ["204", "310", "415"]}


def check_guest_history(phone_number: str = "", **_) -> dict:
    record = GUEST_DB.get(phone_number, {"vip": False, "recent_issues": 0})
    return {"phone_number": phone_number, **record}


def check_room_availability(**_) -> dict:
    return {"available_rooms": list(ROOM_INVENTORY["available_rooms"])}


def dispatch_technician(issue_type: str = "unspecified", **_) -> dict:
    return {"status": "dispatched", "issue_type": issue_type}


def reassign_guest(new_room: str = "", **_) -> dict:
    if new_room in ROOM_INVENTORY["available_rooms"]:
        ROOM_INVENTORY["available_rooms"].remove(new_room)
        return {"status": "reassigned", "new_room": new_room}
    return {"status": "failed", "reason": "room_not_available", "requested_room": new_room}


def escalate_to_manager(reason: str = "unspecified", **_) -> dict:
    return {"status": "escalated", "reason": reason}


TOOL_FUNCTIONS = {
    "check_guest_history": check_guest_history,
    "check_room_availability": check_room_availability,
    "dispatch_technician": dispatch_technician,
    "reassign_guest": reassign_guest,
    "escalate_to_manager": escalate_to_manager,
}
