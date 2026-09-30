def verify_recovery(
    automation_name: str,
    recovery_status: str
) -> dict:

    if recovery_status == "HEALTHY":
        return {
            "automation_name": automation_name,
            "verified": True,
            "status": "HEALTHY"
        }

    return {
        "automation_name": automation_name,
        "verified": False,
        "status": recovery_status
    }