from app.services.recovery_service import execute_recovery
from app.services.verification_service import verify_recovery


def test_ocr_first_attempt_fails_verification():
    recovery = execute_recovery(
        action="RETRY_OCR",
        automation_name="InvoiceProcessingBot",
        attempt_number=1
    )

    verification = verify_recovery(
        automation_name="InvoiceProcessingBot",
        recovery_status=recovery["status"]
    )

    assert recovery["status"] == "FAILED"
    assert verification["verified"] is False


def test_ocr_second_attempt_recovers():
    recovery = execute_recovery(
        action="RETRY_OCR",
        automation_name="InvoiceProcessingBot",
        attempt_number=2
    )

    verification = verify_recovery(
        automation_name="InvoiceProcessingBot",
        recovery_status=recovery["status"]
    )

    assert recovery["status"] == "HEALTHY"
    assert verification["verified"] is True


def test_queue_first_attempt_fails():
    recovery = execute_recovery(
        action="RETRY_QUEUE_CONNECTION",
        automation_name="OrderProcessingBot",
        attempt_number=1
    )

    assert recovery["status"] == "FAILED"


def test_queue_second_attempt_recovers():
    recovery = execute_recovery(
        action="RETRY_QUEUE_CONNECTION",
        automation_name="OrderProcessingBot",
        attempt_number=2
    )

    assert recovery["status"] == "HEALTHY"


def test_credential_refresh_recovers():
    recovery = execute_recovery(
        action="REFRESH_CREDENTIAL",
        automation_name="PaymentReconciliationBot"
    )

    verification = verify_recovery(
        automation_name="PaymentReconciliationBot",
        recovery_status=recovery["status"]
    )

    assert recovery["status"] == "HEALTHY"
    assert verification["verified"] is True