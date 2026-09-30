import uuid

from langgraph.types import Command
from app.agent.workflow import incident_workflow


def run_incident(incident_id: str, approval_decision: str | None = None):

    thread_id = f"incident-{uuid.uuid4()}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "incident_id": incident_id,
        "retry_count": 0,
        "allowed": False,
        "approval_required": False
    }

    result = incident_workflow.invoke(
        initial_state,
        config=config
    )

    print("\n--- WORKFLOW STATE ---")
    print("Incident:", incident_id)
    print("Result:", result.get("final_result"))
    print("Action:", result.get("action"))
    print("Retry count:", result.get("retry_count"))
    print("Recovery status:", result.get("recovery_status"))
    print("Verification passed:", result.get("verification_passed"))
    print("Approval required:", result.get("approval_required"))
    print("Duration:", result.get("duration_seconds"))

    if result.get("approval_required") and approval_decision:

        print("\nHuman decision:", approval_decision)

        result = incident_workflow.invoke(
            Command(resume=approval_decision),
            config=config
        )

        print("\n--- FINAL STATE ---")
        print("Result:", result.get("final_result"))
        print("Action:", result.get("action"))
        print("Retry count:", result.get("retry_count"))
        print("Recovery status:", result.get("recovery_status"))
        print("Verification passed:", result.get("verification_passed"))
        print("Duration:", result.get("duration_seconds"))

    return result


if __name__ == "__main__":
    run_incident(
        incident_id="INC-1001"
    )