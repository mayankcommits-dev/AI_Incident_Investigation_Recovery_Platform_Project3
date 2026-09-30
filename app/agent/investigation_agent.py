import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from app.services.incident_service import get_incident
from app.services.operations_service import (
    get_automation_health,
    get_automation_logs)
from app.rag.retriever import retrieve_runbooks

load_dotenv()

_model = None


def get_investigation_model():
    global _model

    if _model is None:
        _model = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

    return _model


SYSTEM_PROMPT = """
You are an enterprise automation incident investigation assistant.

You will receive evidence that has already been collected from enterprise
systems and runbooks.

Your job is to:
1. Analyze the provided incident details.
2. Analyze automation health and recent logs.
3. Use the retrieved runbook guidance.
4. Explain the likely cause of the incident.
5. Recommend the appropriate recovery approach.

Rules:
- Base factual claims only on the provided evidence.
- Do not invent incident details, logs, health information, or runbook instructions.
- You may recommend recovery actions, but must not claim that you executed them.
- Recovery execution is controlled by deterministic application logic outside the LLM.
"""


def investigate_incident(incident_id: str):

    incident = get_incident(incident_id)

    if incident is None:
        return {
            "investigation": "",
            "evidence": "",
            "error": "INCIDENT_NOT_FOUND"
        }

    health = get_automation_health(
        incident.automation_name
    )

    logs = get_automation_logs(
        incident.automation_name
    )

    runbooks = retrieve_runbooks(
        query=f"{incident.error_code} {incident.error_message}",
        top_k=2
    )

    runbook_text = "\n".join(
        chunk["text"] for chunk in runbooks
    )

    evidence = f"""
INCIDENT:
{incident.model_dump()}

AUTOMATION HEALTH:
{health}

RECENT LOGS:
{logs}

RETRIEVED RUNBOOK:
{runbook_text}
"""

    model = get_investigation_model()

    response = model.invoke(
        f"""
{SYSTEM_PROMPT}

EVIDENCE:
{evidence}

Produce the incident investigation and recommended recovery approach.
"""
    )

    return {
        "investigation": response.content,
        "evidence": evidence
    }
