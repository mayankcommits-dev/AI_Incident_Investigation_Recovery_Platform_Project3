from fastapi.testclient import TestClient
from unittest.mock import patch

from app.api.main import app


client = TestClient(app)


MOCK_INVESTIGATION = {
    "investigation": "Mock investigation based on incident evidence.",
    "evidence": "Mock evidence."
}


@patch(
    "app.agent.workflow.investigate_incident",
    return_value=MOCK_INVESTIGATION
)
def test_ocr_incident_api_recovers(mock_investigation):

    response = client.post(
        "/incidents/investigate",
        json={"incident_id": "INC-1001"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["final_result"] == "RECOVERED"
    assert data["action"] == "RETRY_OCR"
    assert data["retry_count"] == 2
    assert data["recovery_status"] == "HEALTHY"


@patch(
    "app.agent.workflow.investigate_incident",
    return_value=MOCK_INVESTIGATION
)
def test_authentication_api_requires_approval(mock_investigation):

    response = client.post(
        "/incidents/investigate",
        json={"incident_id": "INC-1002"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_required"] is True
    assert data["final_result"] is None
    assert data["thread_id"] is not None


def test_invalid_approval_decision():

    response = client.post(
        "/incidents/fake-thread/approval",
        json={"decision": "maybe"}
    )

    assert response.status_code == 400


@patch(
    "app.agent.workflow.investigate_incident",
    return_value=MOCK_INVESTIGATION
)
def test_authentication_full_hitl_api_flow(mock_investigation):

    # 1. Start investigation
    response = client.post(
        "/incidents/investigate",
        json={"incident_id": "INC-1002"}
    )

    assert response.status_code == 200

    data = response.json()

    assert data["approval_required"] is True
    assert data["final_result"] is None

    thread_id = data["thread_id"]

    # 2. Human approves using same workflow thread
    approval_response = client.post(
        f"/incidents/{thread_id}/approval",
        json={"decision": "approved"}
    )

    assert approval_response.status_code == 200

    result = approval_response.json()

    # 3. Recovery should complete
    assert result["decision"] == "approved"
    assert result["final_result"] == "RECOVERED"
    assert result["action"] == "REFRESH_CREDENTIAL"
    assert result["recovery_status"] == "HEALTHY"
    assert result["retry_count"] == 0


def test_approval_with_unknown_thread_id_returns_404():

    response = client.post(
        "/incidents/non-existent-thread/approval",
        json={"decision": "approved"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "Workflow checkpoint not found for this thread_id."
    )