from app.services.policy_service import evaluate_recovery_policy


def test_ocr_first_retry_allowed():
    result = evaluate_recovery_policy(
        error_code="OCR_TIMEOUT",
        retry_count=0
    )

    assert result["action"] == "RETRY_OCR"
    assert result["allowed"] is True
    assert result["approval_required"] is False


def test_ocr_after_two_retries_escalates():
    result = evaluate_recovery_policy(
        error_code="OCR_TIMEOUT",
        retry_count=2
    )

    assert result["action"] == "ESCALATE"
    assert result["allowed"] is False


def test_authentication_requires_approval():
    result = evaluate_recovery_policy(
        error_code="AUTH_TOKEN_EXPIRED",
        retry_count=0
    )

    assert result["action"] == "REFRESH_CREDENTIAL"
    assert result["allowed"] is True
    assert result["approval_required"] is True


def test_queue_first_retry_is_automatic():
    result = evaluate_recovery_policy(
        error_code="QUEUE_CONNECTION_TIMEOUT",
        retry_count=0
    )

    assert result["action"] == "RETRY_QUEUE_CONNECTION"
    assert result["allowed"] is True
    assert result["approval_required"] is False


def test_queue_second_retry_requires_approval():
    result = evaluate_recovery_policy(
        error_code="QUEUE_CONNECTION_TIMEOUT",
        retry_count=1
    )

    assert result["action"] == "RETRY_QUEUE_CONNECTION"
    assert result["allowed"] is True
    assert result["approval_required"] is True


def test_queue_after_two_retries_escalates():
    result = evaluate_recovery_policy(
        error_code="QUEUE_CONNECTION_TIMEOUT",
        retry_count=2
    )

    assert result["action"] == "ESCALATE"
    assert result["allowed"] is False


def test_unknown_error_defaults_to_escalation():
    result = evaluate_recovery_policy(
        error_code="UNKNOWN_ERROR",
        retry_count=0
    )

    assert result["action"] == "ESCALATE"
    assert result["allowed"] is False