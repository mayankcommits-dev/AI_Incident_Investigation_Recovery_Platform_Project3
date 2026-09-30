import uuid
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langgraph.types import Command
from app.agent.workflow import incident_workflow


app = FastAPI(
    title="AI Incident Investigation & Recovery Platform",
    version="1.0.0"
)


class IncidentRequest(BaseModel):
    incident_id: str

class ApprovalRequest(BaseModel):
    decision: str



@app.post("/incidents/investigate")
def investigate_incident_api(request: IncidentRequest):

    thread_id = f"incident-{uuid.uuid4()}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "incident_id": request.incident_id,
        "retry_count": 0,
        "allowed": False,
        "approval_required": False
    }

    result = incident_workflow.invoke(
        initial_state,
        config=config
    )

    return {
        "thread_id": thread_id,
        "incident_id": request.incident_id,
        "final_result": result.get("final_result"),
        "action": result.get("action"),
        "approval_required": result.get("approval_required"),
        "retry_count": result.get("retry_count"),
        "recovery_status": result.get("recovery_status")
    }


@app.post("/incidents/{thread_id}/approval")
def submit_approval(
    thread_id: str,
    request: ApprovalRequest
):
    decision = request.decision.lower()

    if decision not in {"approved", "rejected"}:
        raise HTTPException(
        status_code=400,
        detail="Decision must be 'approved' or 'rejected'."
    )

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    try:
        result = incident_workflow.invoke(
            Command(resume=decision),
            config= config
        )
    except Exception:
        raise HTTPException(
            status_code=404,
            detail="Workflow checkpoint not found for this thread_id."
        )
    return {
        "thread_id": thread_id,
        "decision": decision,
        "final_result": result.get("final_result"),
        "action": result.get("action"),
        "recovery_status": result.get("recovery_status"),
        "retry_count": result.get("retry_count")
    }