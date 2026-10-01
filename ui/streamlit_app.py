import os
import sys
import uuid

# Force project root to be searched before ui/
PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

# Remove it first if already present, then force it to position 0
if PROJECT_ROOT in sys.path:
    sys.path.remove(PROJECT_ROOT)

sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
from langgraph.types import Command
from app.rag.ingest import ensure_runbooks_ingested
from app.agent.workflow import incident_workflow

st.set_page_config(
    page_title="AI Incident Investigation & Recovery Platform",
    page_icon="🛠️",
    layout="wide"
)

# Initialize the RAG knowledge base on a fresh cloud deployment.
@st.cache_resource
def initialize_knowledge_base():
    ensure_runbooks_ingested()


initialize_knowledge_base()


st.title("AI Incident Investigation & Recovery Platform")

st.caption(
    "AI-assisted investigation and controlled recovery "
    "for enterprise automation incidents."
)

# Clearly state the safety boundary of the portfolio demo
st.info(
    "Portfolio Demo: AI investigation, RAG, policy decisions, "
    "human approval and workflow orchestration are implemented end-to-end. "
    "External operational recovery actions are safely simulated."
)


# Preserve workflow information across Streamlit reruns
if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None

if "thread_id" not in st.session_state:
    st.session_state.thread_id = None


# Display the current workflow state
def display_workflow_result(result):

    st.subheader("AI Investigation")

    investigation = result.get("investigation")

    if investigation:
        st.write(investigation)
    else:
        st.info("No investigation details available.")

    st.divider()

    st.subheader("Recovery Decision")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Proposed Action",
            result.get("action") or "N/A"
        )

    with col2:
        st.metric(
            "Retries",
            result.get("retry_count", 0)
        )

    # Show approval requirement or final human decision
    with col3:

        decision = result.get("decision")

        if decision == "approved":
            approval_text = "Approved"

        elif decision == "rejected":
            approval_text = "Rejected"

        elif result.get("approval_required"):
            approval_text = "Required"

        else:
            approval_text = "Not Required"

        st.metric(
            "Human Approval",
            approval_text
        )

    st.divider()

    st.subheader("Recovery Status")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Result",
            result.get("final_result") or "Pending"
        )

    with col2:
        st.metric(
            "System Status",
            result.get("recovery_status") or "Pending"
        )

    verification = result.get("verification_passed")

    if verification is True:
        verification_text = "Passed"

    elif verification is False:
        verification_text = "Failed"

    else:
        verification_text = "Pending"

    with col3:
        st.metric(
            "Verification",
            verification_text
        )

    duration = result.get("duration_seconds")

    if duration is not None:
        st.caption(
            f"End-to-end workflow duration: {duration:.3f} seconds"
        )


incident_id = st.selectbox(
    "Select an incident",
    [
        "INC-1001 — OCR Processing Timeout",
        "INC-1002 — Authentication Token Expired",
        "INC-1003 — Queue Connection Timeout"
    ]
)


# Start a new investigation
if st.button(
    "Investigate Incident",
    type="primary"
):

    selected_incident_id = incident_id.split(" — ")[0]

    # Every investigation receives its own LangGraph thread
    thread_id = f"incident-{uuid.uuid4()}"

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    initial_state = {
        "incident_id": selected_incident_id,
        "retry_count": 0,
        "allowed": False,
        "approval_required": False
    }

    with st.spinner(
        "Investigating incident and evaluating recovery policy..."
    ):

        try:

            # Public demo invokes the same LangGraph workflow directly
            result = incident_workflow.invoke(
                initial_state,
                config=config
            )

            # Save checkpoint identity and workflow state across UI reruns
            st.session_state.thread_id = thread_id
            st.session_state.workflow_result = result

            st.success(
                "Investigation completed."
            )

        except Exception as error:

            st.error(
                f"Investigation failed: {error}"
            )


# Recover the current workflow state after Streamlit reruns
result = st.session_state.workflow_result


if result:

    display_workflow_result(result)


# HITL controls appear only when the workflow is paused for approval
if (
    result
    and result.get("approval_required")
    and not result.get("final_result")
):

    st.warning(
        "Human approval is required before the proposed "
        "recovery action can execute."
    )

    st.write(
        f"**Proposed sensitive action:** "
        f"`{result.get('action')}`"
    )

    approve_col, reject_col = st.columns(2)

    with approve_col:

        approve = st.button(
            "Approve Recovery",
            type="primary"
        )

    with reject_col:

        reject = st.button(
            "Reject Recovery"
        )

    decision = None

    if approve:
        decision = "approved"

    elif reject:
        decision = "rejected"


    if decision:

        thread_id = st.session_state.thread_id

        config = {
            "configurable": {
                "thread_id": thread_id
            }
        }

        with st.spinner(
            f"Submitting {decision} decision..."
        ):

            try:

                # Resume the exact paused LangGraph workflow
                resumed_result = incident_workflow.invoke(
                    Command(resume=decision),
                    config=config
                )

                # API previously returned this field explicitly.
                # Add it to the UI state so approval status displays correctly.
                resumed_result["decision"] = decision

                st.session_state.workflow_result = resumed_result

                st.rerun()

            except Exception as error:

                st.error(
                    f"Unable to resume workflow: {error}"
                )