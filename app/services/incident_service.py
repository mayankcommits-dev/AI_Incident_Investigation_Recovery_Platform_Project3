import json
from pathlib import Path

from app.models.incident import Incident


project_root = Path(__file__).resolve().parent.parent.parent
incident_file = project_root / "data" / "incidents" / "incidents.json"


def load_incidents():
    with open(incident_file, "r") as file:
        data = json.load(file)

    incidents = []

    for item in data:
        incident = Incident(**item) 
        incidents.append(incident)

    return incidents


#Retrieve one incident
def get_incident(incident_id):
    incidents = load_incidents()

    for incident in incidents:
        if incident.incident_id == incident_id:
            return incident

    return None

incident = get_incident("INC-1002")

