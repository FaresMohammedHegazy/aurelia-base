def dispatch_maintenance(issue):

    print(f"  -> TOOL: Dispatching Maintenance")
    print(f"  -> ISSUE: {issue}")

    return "Maintenance team notified."


def dispatch_hvac(issue):

    print(f"  -> TOOL: Dispatching HVAC Technician")
    print(f"  -> ISSUE: {issue}")

    return "HVAC technician notified."


def dispatch_security(issue):

    print(f"  -> TOOL: Dispatching Security")
    print(f"  -> ISSUE: {issue}")

    return "Security notified."


def escalate_manager(issue):

    print(f"  -> TOOL: Escalating to Front Desk Manager")
    print(f"  -> ISSUE: {issue}")

    return "Manager notified."
