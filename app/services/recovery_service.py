def retry_ocr(automation_name: str, attempt_number: int) -> dict:
    if attempt_number >= 2:
        status = "HEALTHY"
    else:
        status = "FAILED"

    return {
        "action": "RETRY_OCR",
        "automation_name": automation_name,
        "executed": True,
        "status": status
    }


def retry_queue_connection(automation_name: str, attempt_number: int) -> dict:
    if attempt_number >= 2:
        status = "HEALTHY"
    else:
        status = "FAILED"

    return {
        "action": "RETRY_QUEUE_CONNECTION",
        "automation_name": automation_name,
        "executed": True,
        "status": status
    }


def refresh_credential(automation_name: str) -> dict:
    return {
        "action": "REFRESH_CREDENTIAL",
        "automation_name": automation_name,
        "executed": True,
        "status": "HEALTHY"
    }


def execute_recovery(
    action: str,
    automation_name: str,
    attempt_number: int = 1
) -> dict:

    if action == "RETRY_OCR":
        return retry_ocr(automation_name, attempt_number)

    if action == "RETRY_QUEUE_CONNECTION":
        return retry_queue_connection(automation_name, attempt_number)

    if action == "REFRESH_CREDENTIAL":
        return refresh_credential(automation_name)

    return {
        "action": action,
        "automation_name": automation_name,
        "executed": False,
        "status": "ESCALATED"
    }

