from mcp.server.mcpserver import MCPServer

from app.services.incident_service import get_incident
from app.services.operations_service import (
    get_automation_health,
    get_automation_logs
)


mcp = MCPServer("IncidentOperationsServer")


@mcp.tool()
def get_incident_information(incident_id: str) -> dict:
    """Retrieve information about an automation incident."""

    incident = get_incident(incident_id)

    if incident is None:
        return {
            "error": "INCIDENT_NOT_FOUND"
        }

    return incident.model_dump()


@mcp.tool()
def check_automation_status(automation_name: str) -> dict:
    """Retrieve the current health of an automation."""

    return get_automation_health(automation_name)


@mcp.tool()
def get_operational_logs(automation_name: str) -> list:
    """Retrieve recent operational logs for an automation."""

    return get_automation_logs(automation_name)


if __name__ == "__main__":
    mcp.run()