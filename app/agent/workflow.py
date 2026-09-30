from langgraph.graph import StateGraph, START, END

from app.services.incident_service import get_incident
from app.services.policy_service import evaluate_recovery_policy
from app.services.recovery_service import execute_recovery
from app.agent.investigation_agent import investigate_incident

from typing import TypedDict, Optional
from langgraph.types import interrupt
from langgraph.checkpoint.memory import InMemorySaver
from app.services.verification_service import verify_recovery
import time

class IncidentWorkflowState(TypedDict):
    incident_id: str
    automation_name: Optional[str]
    error_code: Optional[str]
    retry_count: int
    start_time: Optional[float]
    duration_seconds: Optional[float]
    investigation: Optional[str]
    
    action: Optional[str]
    allowed: bool
    approval_required: bool
    approval_decision: Optional[str]
    verification_passed: bool

    recovery_status: Optional[str]
    final_result: Optional[str]


def load_incident_node(state: IncidentWorkflowState):
    start_time = time.perf_counter()
    incident = get_incident(state["incident_id"])

    if incident is None:
        return {
        "final_result": "INCIDENT_NOT_FOUND",
        "start_time": start_time,
        "duration_seconds": round(
            time.perf_counter() - start_time, 3
        )
    }

    return {
        "automation_name": incident.automation_name,
        "error_code": incident.error_code,
        "retry_count": incident.retry_count,
        "start_time": start_time,
    }

def route_after_load(state: IncidentWorkflowState):
    if state.get("final_result") == "INCIDENT_NOT_FOUND":
        return "not_found"

    return "continue"


def investigate_node(state: IncidentWorkflowState):
    result = investigate_incident(state["incident_id"])

    return {
        "investigation": result["investigation"]
    }


def policy_node(state: IncidentWorkflowState):
    policy = evaluate_recovery_policy(
        error_code=state["error_code"],
        retry_count=state["retry_count"]
    )

    return {
        "action": policy["action"],
        "allowed": policy["allowed"],
        "approval_required": policy["approval_required"]
    }


def route_after_policy(state: IncidentWorkflowState):
    if not state["allowed"]:
        return "blocked"

    if state["approval_required"]:
        return "approval"

    return "execute"


def approval_node(state: IncidentWorkflowState):
    decision = interrupt({
        "incident_id": state["incident_id"],
        "automation_name": state["automation_name"],
        "action": state["action"],
        "message": "Human approval required before recovery execution."
    })

    return {
        "approval_decision": decision
    }

def route_after_approval(state: IncidentWorkflowState):
    if state["approval_decision"] == "approved":
        return "execute"

    return "rejected"

def execute_recovery_node(state: IncidentWorkflowState):
    action = state["action"]

    retry_actions = {
        "RETRY_OCR",
        "RETRY_QUEUE_CONNECTION"
    }

    if action in retry_actions:
        attempt_number = state["retry_count"] + 1
        new_retry_count = attempt_number
    else:
        attempt_number = 1
        new_retry_count = state["retry_count"]

    result = execute_recovery(
        action=action,
        automation_name=state["automation_name"],
        attempt_number=attempt_number
    )

    return {
        "retry_count": new_retry_count,
        "recovery_status": result["status"]
    }

def route_after_verification(state: IncidentWorkflowState):

    if state["verification_passed"]:
        return "recovered"

    return "retry"

def recovered_node(state: IncidentWorkflowState):

    duration = time.perf_counter() - state["start_time"]

    return {
        "final_result": "RECOVERED",
        "duration_seconds": round(duration, 3)
    }


def escalated_node(state: IncidentWorkflowState):

    duration = time.perf_counter() - state["start_time"]

    return {
        "final_result": "ESCALATED",
        "duration_seconds": round(duration, 3)
    }


def rejected_node(state: IncidentWorkflowState):

    duration = time.perf_counter() - state["start_time"]

    return {
        "final_result": "REJECTED",
        "duration_seconds": round(duration, 3)
    }


def verify_recovery_node(state: IncidentWorkflowState):

    result = verify_recovery(
        automation_name=state["automation_name"],
        recovery_status=state["recovery_status"]
    )

    return {
        "verification_passed": result["verified"]
    }

workflow = StateGraph(IncidentWorkflowState)

workflow.add_node("load_incident", load_incident_node)
workflow.add_node("investigate", investigate_node)
workflow.add_node("policy", policy_node)
workflow.add_node("approval", approval_node)
workflow.add_node("execute_recovery", execute_recovery_node)
workflow.add_node("recovered", recovered_node)
workflow.add_node("escalated", escalated_node)
workflow.add_node("rejected", rejected_node)
workflow.add_node("verify_recovery", verify_recovery_node)




workflow.add_edge(START, "load_incident")
workflow.add_conditional_edges(
    "load_incident",
    route_after_load,
    {
        "continue": "investigate",
        "not_found": END
    }
)
workflow.add_edge("investigate", "policy")

workflow.add_conditional_edges(
    "policy",
    route_after_policy,
    {
        "blocked": "escalated",
        "approval": "approval",
        "execute": "execute_recovery"
    }
)


workflow.add_conditional_edges(
    "approval",
    route_after_approval,
    {
        "execute": "execute_recovery",
        "rejected": "rejected"
    }
)

workflow.add_edge(
    "execute_recovery",
    "verify_recovery"
)

workflow.add_conditional_edges(
    "verify_recovery",
    route_after_verification,
    {
        "recovered": "recovered",
        "retry": "policy"
    }
)


workflow.add_edge("recovered", END)
workflow.add_edge("escalated", END)
workflow.add_edge("rejected", END)


checkpointer = InMemorySaver()

incident_workflow = workflow.compile(
    checkpointer=checkpointer
)