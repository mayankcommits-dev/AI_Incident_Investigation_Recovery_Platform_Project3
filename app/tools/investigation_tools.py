from langchain_core.tools import tool

from app.services.incident_service import get_incident
from app.services.operations_service import (
    get_automation_health,
    get_automation_logs
)
from app.rag.retriever import retrieve_runbooks


@tool
def get_incident_details(incident_id: str) -> dict:
    """Get details for a specific incident ID."""

    incident = get_incident(incident_id)

    if incident is None:
        return {"error": "Incident not found"}

    return incident.model_dump()


@tool
def check_automation_health(automation_name: str) -> dict:
    """Check the current health of an automation."""

    health = get_automation_health(automation_name)

    if health is None:
        return {"error": "Automation not found"}

    return health


@tool
def get_recent_logs(automation_name: str) -> list[str]:
    """Get recent operational logs for an automation."""

    return get_automation_logs(automation_name)


@tool
def search_runbooks(query: str) -> list[dict]:
    """Search enterprise runbooks for information relevant to an incident."""

    return retrieve_runbooks(
        query=query,
        top_k=2
    )


investigation_tools = [
    get_incident_details,
    check_automation_health,
    get_recent_logs,
    search_runbooks
]


