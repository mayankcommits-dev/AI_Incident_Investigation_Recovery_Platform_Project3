from pydantic import BaseModel
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

class EvaluationResult(BaseModel):
    score: float
    reason: str

load_dotenv()

_model = None


def get_judge_model():

    global _model

    if _model is None:
        model = ChatGroq(
            model="openai/gpt-oss-20b",
            temperature=0,
            api_key=os.getenv("GROQ_API_KEY")
        )

        _model = model.with_structured_output(
    EvaluationResult,
    method="json_schema")

    return _model


def evaluate_relevance(
    incident_details: str,
    investigation: str
) -> EvaluationResult:

    judge = get_judge_model()

    prompt = f"""
You are evaluating an AI-generated incident investigation.

INCIDENT:
{incident_details}

AI INVESTIGATION:
{investigation}

Evaluate whether the investigation is relevant to the incident.

Score from 0.0 to 1.0:
1.0 = directly addresses the incident and its failure
0.0 = unrelated to the incident

Return a score and a short reason.
"""

    return judge.invoke(prompt)



def evaluate_groundedness(
    evidence: str,
    investigation: str
) -> EvaluationResult:

    judge = get_judge_model()

    prompt = f"""
You are evaluating whether an AI incident investigation is grounded
in the provided evidence.

EVIDENCE:
{evidence}

AI INVESTIGATION:
{investigation}

Check whether factual claims in the investigation are supported by
the evidence.

Score from 0.0 to 1.0:
1.0 = all important factual claims are supported
0.0 = important claims are unsupported or invented

Return a score and a short reason.
"""

    return judge.invoke(prompt)