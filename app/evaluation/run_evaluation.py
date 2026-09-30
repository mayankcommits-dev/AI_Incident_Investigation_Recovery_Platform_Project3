from app.agent.investigation_agent import investigate_incident
from app.services.incident_service import get_incident
from app.evaluation.judges import (
    evaluate_relevance,
    evaluate_groundedness)


RELEVANCE_THRESHOLD = 0.80
GROUNDEDNESS_THRESHOLD = 0.80

def evaluate_incident(incident_id: str):

    # 1. Get incident
    incident = get_incident(incident_id)

    if incident is None:
        print("Incident not found")
        return

    # 2. Run actual AI investigation
    result = investigate_incident(incident_id)

    investigation = result["investigation"]
    evidence = result["evidence"]

    # 4. Evaluate
    relevance = evaluate_relevance(
        incident_details=str(incident.model_dump()),
        investigation=investigation
    )

    groundedness = evaluate_groundedness(
        evidence=evidence,
        investigation=investigation
    )

    passed = (
    relevance.score >= RELEVANCE_THRESHOLD
    and groundedness.score >= GROUNDEDNESS_THRESHOLD)


    # 5. Results
    print("\n--- AI EVALUATION ---")
    print("Incident:", incident_id)

    print("\nRelevance:")
    print("Score:", relevance.score)
    print("Reason:", relevance.reason)

    print("\nGroundedness:")
    print("Score:", groundedness.score)
    print("Reason:", groundedness.reason)

    print("\nQuality Gate:", "PASS" if passed else "FAIL")


if __name__ == "__main__":

    incidents = [
        "INC-1001",
        "INC-1002",
        "INC-1003"
    ]

    for incident_id in incidents:
        evaluate_incident(incident_id)