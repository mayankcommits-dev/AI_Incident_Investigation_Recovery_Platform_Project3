from pydantic import BaseModel


class Incident(BaseModel):
    incident_id: str
    automation_name: str
    status: str
    severity: str
    error_code: str
    error_message: str
    retry_count: int = 0