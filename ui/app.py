import os
import streamlit as st
import requests

# API address can be changed through the deployment environment
API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://localhost:8000"
)

st.set_page_config(
    page_title="AI Incident Investigation & Recovery Platform",
    page_icon="🛠️",
    layout="wide"
)

st.title("AI Incident Investigation & Recovery Platform")

st.caption(
    "AI-assisted investigation and controlled recovery "
    "for enterprise automation incidents."
)

# Clarify that external recovery operations are simulated in this portfolio demo
st.info(
    "Portfolio Demo: Incident investigation uses the AI/RAG workflow, "
    "while external operational recovery actions are safely simulated."
)

# Store workflow result across Streamlit reruns
if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None


# Added reusable result display so results survive reruns
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

        # Show the actual human approval outcome
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
            f"Workflow execution time: {duration} seconds"
        )


incident_id = st.selectbox(
    "Select an incident",
    [
        "INC-1001 — OCR Processing Timeout",
        "INC-1002 — Authentication Token Expired",
        "INC-1003 — Queue Connection Timeout"
    ]
)


if st.button("Investigate Incident", type="primary"):

    selected_incident_id = incident_id.split(" — ")[0]

    with st.spinner("Investigating incident..."):

        try:
            response = requests.post(
                f"{API_BASE_URL}/incidents/investigate",
                json={"incident_id": selected_incident_id},
                timeout=60
            )

            response.raise_for_status()
            result = response.json()

            # Save latest workflow state for later reruns
            st.session_state.workflow_result = result

            st.success("Investigation completed.")

        except requests.RequestException as error:
            st.error(
                f"Unable to contact investigation service: {error}"
            )


# Load saved result even after Streamlit reruns
result = st.session_state.workflow_result


# Display saved workflow result
if result:
    display_workflow_result(result)


# Show HITL controls only while workflow is waiting
if result and result.get("approval_required") and not result.get("final_result"):

    st.warning(
        "Human approval is required before the proposed recovery action can execute."
    )

    st.write(
        f"**Proposed sensitive action:** `{result.get('action')}`"
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

        thread_id = result["thread_id"]

        with st.spinner(
            f"Submitting {decision} decision..."
        ):

            try:
                response = requests.post(
                    f"{API_BASE_URL}/incidents/{thread_id}/approval",
                    json={"decision": decision},
                    timeout=60
                )

                response.raise_for_status()

                resumed_result = response.json()

                # Replace paused state with resumed workflow result
                st.session_state.workflow_result = resumed_result

                # Rerun UI using the new saved result
                st.rerun()

            except requests.RequestException as error:
                st.error(
                    f"Unable to submit approval decision: {error}"
                )