# AI Incident Investigation & Recovery Platform

An end-to-end Agentic AI application for investigating enterprise automation incidents and performing controlled recovery using RAG, LLM reasoning, deterministic policy controls, human-in-the-loop approval, and explicit post-recovery verification.

## 🚀 Live Demo

**Try the deployed application:**  
https://aiincidentinvestigationrecoveryplatformproject3-hjvmdremvo2gwb.streamlit.app/

> **Portfolio Demo:** AI investigation, RAG, policy decisions, human approval, workflow orchestration, and verification are implemented end-to-end. External operational recovery actions are safely simulated.

---

## Problem Statement

Enterprise automation failures often require engineers to manually inspect logs, check system health, search operational runbooks, determine an appropriate recovery action, and verify whether the system recovered successfully.

This project demonstrates an AI-assisted incident recovery architecture where:

- operational evidence is collected automatically,
- relevant runbooks are retrieved using RAG,
- an LLM investigates the incident,
- deterministic policies decide which actions are permitted,
- sensitive operations require human approval,
- recovery is bounded by retry policies,
- and recovery is explicitly verified before an incident is considered resolved.

The LLM **does not independently authorize operational actions**.

---

## Architecture

### Production / API Architecture

```text
Incident / Automation Failure
            |
            v
        FastAPI API
            |
            v
    Load & Validate Incident
            |
            v
Deterministic Evidence Collection
    |       |       |       |
 Incident Health   Logs    RAG Runbook
            |
            v
   LLM Investigation
            |
            v
  Deterministic Policy
      /       |       \
   BLOCK   APPROVAL   SAFE ACTION
              |
              v
       Human Approval
              |
              v
      Controlled Recovery
              |
              v
    Explicit Verification
              |
              v
 Retry / Success / Escalation
              |
              v
      Telemetry + Result
```

### Public Demo Architecture

```text
User
 |
 v
Streamlit Community Cloud
 |
 v
LangGraph Workflow
 |---- RAG / ChromaDB
 |---- Groq LLM
 |---- Deterministic Policy
 |---- Human-in-the-Loop
 |---- Simulated Recovery
 |---- Verification
 |
 v
Final Incident Result
```

The public portfolio demo invokes the workflow directly from Streamlit, while the repository also contains a FastAPI interface representing the API-oriented application architecture.

---

## Incident Scenarios

| Incident | Failure | Recovery Behaviour |
|---|---|---|
| INC-1001 | OCR Timeout | Bounded autonomous retry followed by verification |
| INC-1002 | Authentication Token Expired | Credential refresh requires human approval |
| INC-1003 | Queue Connection Timeout | First retry automatic; second retry requires human approval |

This demonstrates different levels of autonomy depending on operational risk.

---

## Key Features

- LangGraph-based stateful incident recovery workflow
- Retrieval-Augmented Generation (RAG) over operational runbooks
- SentenceTransformer embeddings with ChromaDB vector retrieval
- Groq-powered LLM investigation
- Deterministic recovery policy and authorization layer
- Human-in-the-loop approval for sensitive actions
- Bounded retry and escalation logic
- Explicit post-recovery verification
- FastAPI incident investigation and approval endpoints
- Read-only MCP operational tools
- Runtime telemetry and workflow-state tracking
- Streamlit interactive portfolio application
- Dockerized application
- GitHub Actions CI pipeline
- Automated unit, workflow, and API testing

---

## Evaluation & Testing

The project includes separate evaluation and automated testing layers.

### AI / RAG Evaluation

Current evaluation dataset results:

- **Average Relevance: 96.7%**
- **Average Groundedness: 98.3%**

The evaluation pipeline measures whether generated investigations are relevant to the incident and grounded in the evidence supplied to the model.

Retrieval behavior was also calibrated using similarity-distance thresholds to reject unsupported queries.

### Automated Testing

**22 automated tests** cover:

- deterministic recovery policies,
- recovery and verification logic,
- LangGraph workflow behavior,
- human approval paths,
- retry behavior,
- and FastAPI endpoints.

LLM calls are mocked in deterministic workflow tests, while real-model behavior is evaluated separately.

---

## Safety & Control Design

The application intentionally separates **AI reasoning** from **operational authorization**.

```text
LLM
 |
 | investigates + recommends
 v
Deterministic Policy
 |
 | authorizes / blocks / requests approval
 v
Human Approval (when required)
 |
 v
Recovery Service
 |
 v
Verification
```

The LLM can investigate incidents and recommend recovery actions, but it cannot independently authorize sensitive recovery operations.

Sensitive credential recovery requires human approval, and recovery actions are explicitly verified before the workflow reports success.

MCP exposes read-only operational capabilities; sensitive recovery operations are deliberately not exposed as unrestricted MCP tools.

---

## Technology Stack

**AI / Agentic AI**
- LangGraph
- Groq LLM
- RAG
- SentenceTransformers
- ChromaDB
- MCP
- Structured AI evaluation

**Backend**
- Python
- FastAPI
- Pydantic
- REST APIs

**Production Engineering**
- Docker
- GitHub Actions CI/CD
- Pytest
- Environment / secrets management
- Logging and telemetry

**Frontend / Demo**
- Streamlit

---

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/mayankcommits-dev/AI_Incident_Investigation_Recovery_Platform_Project3.git
cd AI_Incident_Investigation_Recovery_Platform_Project3
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Never commit the real `.env` file.

### 4. Ingest runbooks

```bash
py -m app.rag.ingest
```

### 5. Run the Streamlit demo

```bash
py -m streamlit run ui/streamlit_app.py --server.fileWatcherType none
```

### 6. Run the FastAPI interface

```bash
py -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```

### 7. Run automated tests

```bash
py -m pytest -v
```

---

## Docker

Build the image:

```bash
docker build -t ai-incident-platform .
```

Run the container with runtime secrets:

```bash
docker run --env-file .env -p 8000:8000 ai-incident-platform
```

The container initializes the runbook knowledge base before starting the API server.

---

## CI/CD

GitHub Actions runs the project in a clean environment by:

1. checking out the repository,
2. configuring Python,
3. installing dependencies,
4. ingesting the runbook knowledge base,
5. running the automated test suite.

This prevents the CI pipeline from depending on locally generated ChromaDB state.

---

## Engineering Design Decisions

### Why deterministic evidence collection?

An earlier agent-directed approach could terminate before collecting all required operational evidence. The final architecture therefore collects mandatory incident details, health information, logs, and RAG context deterministically before LLM reasoning.

### Why doesn't the LLM execute recovery directly?

A syntactically valid tool call does not mean an action is operationally authorized. Recovery authorization therefore remains deterministic and sensitive operations can require human approval.

### Why explicit verification?

Successful execution of a recovery command does not prove that the underlying automation recovered. The workflow separately verifies system health before reporting `RECOVERED`.

### Why separate testing from AI evaluation?

Deterministic application behavior should be reproducible in CI. LLM calls are therefore mocked for workflow tests, while real-model quality is measured through a separate evaluation pipeline.

---

## Project Outcome

The final system demonstrates the complete lifecycle of an AI-assisted operational workflow:

```text
Detect
  -> Gather Evidence
  -> Retrieve Knowledge
  -> Investigate
  -> Apply Policy
  -> Request Approval if Required
  -> Recover
  -> Verify
  -> Retry or Escalate
  -> Report
```

It combines Agentic AI with deterministic engineering controls rather than allowing unrestricted autonomous execution.

---

## Author

**Mayank Jaiswal**

GitHub: https://github.com/mayankcommits-dev


