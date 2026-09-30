from unittest.mock import patch
from uuid import uuid4

from langgraph.types import Command

from app.agent.workflow import incident_workflow


def config():
    return {
        "configurable": {
            "thread_id": f"test-{uuid4()}"
        }
    }


def initial_state(incident_id):
    return {
        "incident_id": incident_id,
        "automation_name": None,
        "error_code": None,
        "retry_count": 0,
        "start_time": None,
        "duration_seconds": None,
        "investigation": None,
        "action": None,
        "allowed": False,
        "approval_required": False,
        "approval_decision": None,
        "recovery_status": None,
        "verification_passed": False,
        "final_result": None
    }


MOCK_INVESTIGATION = {
    "investigation": "Mock investigation based on incident evidence.",
    "evidence": "Mock evidence."
}


@patch(
    "app.agent.workflow.investigate_incident",
    return_value=MOCK_INVESTIGATION
)
def test_ocr_recovers_after_two_attempts(mock_investigation):

    result = incident_workflow.invoke(
        initial_state("INC-1001"),
        config=config()
    )

    assert result["final_result"] == "RECOVERED"
    assert result["action"] == "RETRY_OCR"
    assert result["retry_count"] == 2
    assert result["verification_passed"] is True


@patch(
    "app.agent.workflow.investigate_incident",
    return_value=MOCK_INVESTIGATION
)
def test_authentication_pauses_for_approval(mock_investigation):

    result = incident_workflow.invoke(
        initial_state("INC-1002"),
        config=config()
    )

    assert result["approval_required"] is True
    assert result["final_result"] is None


@patch(
    "app.agent.workflow.investigate_incident",
    return_value=MOCK_INVESTIGATION
)
def test_queue_first_retry_then_requires_approval(mock_investigation):

    result = incident_workflow.invoke(
        initial_state("INC-1003"),
        config=config()
    )

    assert result["approval_required"] is True
    assert result["retry_count"] == 1
    assert result["recovery_status"] == "FAILED"



@patch(
    "app.agent.workflow.investigate_incident",
    return_value=MOCK_INVESTIGATION
)
def test_authentication_approval_recovers(mock_investigation):

    thread_config = config()

    # First request pauses for approval
    paused = incident_workflow.invoke(
        initial_state("INC-1002"),
        config=thread_config
    )

    assert paused["approval_required"] is True
    assert paused["final_result"] is None

    # Human approves
    result = incident_workflow.invoke(
        Command(resume="approved"),
        config=thread_config
    )

    assert result["final_result"] == "RECOVERED"
    assert result["action"] == "REFRESH_CREDENTIAL"
    assert result["recovery_status"] == "HEALTHY"
    assert result["verification_passed"] is True
    assert result["retry_count"] == 0


@patch(
    "app.agent.workflow.investigate_incident",
    return_value=MOCK_INVESTIGATION
)
def test_authentication_rejection_stops_recovery(mock_investigation):

    thread_config = config()

    paused = incident_workflow.invoke(
        initial_state("INC-1002"),
        config=thread_config
    )

    assert paused["approval_required"] is True

    # Human rejects
    result = incident_workflow.invoke(
        Command(resume="rejected"),
        config=thread_config
    )

    assert result["final_result"] == "REJECTED"
    assert result["recovery_status"] is None
    assert result["retry_count"] == 0