def evaluate_recovery_policy(
    error_code: str,
    retry_count: int
) -> dict:

    if error_code == "OCR_TIMEOUT":

        if retry_count < 2:
            return {
                "action": "RETRY_OCR",
                "approval_required": False,
                "allowed": True
            }

        return {
            "action": "ESCALATE",
            "approval_required": False,
            "allowed": False
        }


    if error_code == "AUTH_TOKEN_EXPIRED":
        return {
            "action": "REFRESH_CREDENTIAL",
            "approval_required": True,
            "allowed": True
        }

    if error_code == "QUEUE_CONNECTION_TIMEOUT":

        if retry_count == 0:
            return {
                "action": "RETRY_QUEUE_CONNECTION",
                "approval_required": False,
                "allowed": True
            }

        if retry_count == 1:
            return {
                "action": "RETRY_QUEUE_CONNECTION",
                "approval_required": True,
                "allowed": True
            }

        return {
            "action": "ESCALATE",
            "approval_required": False,
            "allowed": False
        }

    return {
        "action": "ESCALATE",
        "approval_required": False,
        "allowed": False
    }


