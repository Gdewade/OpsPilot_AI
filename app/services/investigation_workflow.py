from typing import TypedDict

# Import the function that analyzes application logs.
from app.services.log_analyzer import analyze_logs

# Import the class that searches runbooks using FAISS and BM25.
from app.services.hybrid_search import HybridRunbookSearch

# Import the tools needed to build a LangGraph workflow.
from langgraph.graph import StateGraph, START, END


class InvestigationState(TypedDict):
    # Stores the incident title.
    # Example: "Payment Service Failure"
    incident_title: str

    # Stores the logs related to the incident.
    # Example: "ERROR: Database connection timeout"
    log_text: str

    # Stores the results of log analysis.
    # Example: error count, warning count, and severity
    log_analysis: dict

    # Stores useful runbook results found by hybrid search.
    # Each result can contain content, source, and score.
    runbook_results: list[dict]

    # Stores the possible reason for the incident.
    # Example: "Database connection timeout"
    root_cause: str

    # Stores information that supports the root cause.
    # Example: important log lines and runbook sources
    evidence: list[str]

    # Tells us whether we have enough evidence.
    # True means enough evidence; False means more investigation is needed.
    evidence_sufficient: bool

    # Stores the current status of the investigation.
    # Example: "completed" or "incomplete"
    investigation_status: str


def log_analysis_node(state: InvestigationState) -> dict:
    """
    Analyze the incident logs and return the results.
    """

    # Get the incident logs from the shared state.
    log_text = state["log_text"]

    # Analyze the logs using our existing function.
    analysis_result = analyze_logs(log_text)

    # Return the analysis results and update the investigation status.
    # LangGraph will merge these updates into the shared state.
    return {
        "log_analysis": analysis_result,
        "investigation_status": "log_analysis_completed",
    }



# Create the runbook search engine.
runbook_search_engine = HybridRunbookSearch()


def runbook_retrieval_node(state: InvestigationState) -> dict:
    """
    Find useful runbooks for the current incident.
    """

    # Get the incident logs from the shared state.
    log_text = state["log_text"]

    # Get the log analysis results.
    log_analysis = state["log_analysis"]

    # Use the incident title, logs, and detected errors to form a search query.
    search_query = (
        f"{state['incident_title']} "
        f"{log_text} "
        f"{' '.join(log_analysis.get('errors', []))}"
    )

    # Build the search indexes if they are not ready yet.
    if runbook_search_engine.vector_index is None:
        runbook_search_engine.build_index()

    # Search for the three most relevant runbook chunks.
    results = runbook_search_engine.search(
        query=search_query,
        k=3,
    )

    # Save the retrieved runbooks in the shared state.
    return {
        "runbook_results": results,
        "investigation_status": "runbook_retrieval_completed",
    }


def rca_investigation_node(state: InvestigationState) -> dict:
    """
    Identify a possible root cause using logs and runbook evidence.
    """

    # Get the analysis results from the shared state.
    log_analysis = state["log_analysis"]

    # Get the runbooks retrieved for this incident.
    runbook_results = state["runbook_results"]

    # Collect the error messages found in the logs.
    errors = log_analysis.get("errors", [])

    # Collect the source names of the retrieved runbooks.
    sources = [
        result["source"]
        for result in runbook_results
        if result.get("source")
    ]

    # Start with a default message if no clear cause is found.
    root_cause = "Possible root cause could not be identified."
    evidence = []

    # Use the first error as an initial clue.
    if errors:
        root_cause = f"Possible cause based on logs: {errors[0]}"
        evidence.extend(errors)

    # Add runbook sources as supporting references.
    if sources:
        evidence.extend(
            [f"Runbook source: {source}" for source in sources]
        )

    # Return the investigation findings.
    return {
        "root_cause": root_cause,
        "evidence": evidence,
        "investigation_status": "rca_investigation_completed",
    }


def evidence_verification_node(state: InvestigationState) -> dict:
    """
    Check whether the investigation has supporting evidence.
    """

    # Get the possible root cause.
    root_cause = state["root_cause"]

    # Get the evidence collected during the investigation.
    evidence = state["evidence"]

    # Check that the root cause is meaningful and evidence exists.
    evidence_sufficient = (
        bool(root_cause.strip())
        and "could not be identified" not in root_cause.lower()
        and len(evidence) > 0
    )

    # Mark the investigation based on the evidence check.
    if evidence_sufficient:
        status = "completed"
    else:
        status = "incomplete"

    # Return the verification result.
    return {
        "evidence_sufficient": evidence_sufficient,
        "investigation_status": status,
    }



def route_after_verification(state: InvestigationState) -> str:
    """
    Choose the next step based on evidence verification.
    """

    # Check whether enough evidence was found.
    if state["evidence_sufficient"]:
        # Continue to the successful end of the investigation.
        return "complete"

    # Stop with an incomplete status when evidence is insufficient.
    return "incomplete"


def build_investigation_workflow():
    """
    Connect all investigation nodes into one workflow.
    """

    # Create a workflow using our shared state structure.
    workflow = StateGraph(InvestigationState)

    # Register each node with the workflow.
    workflow.add_node("log_analysis", log_analysis_node)
    workflow.add_node("runbook_retrieval", runbook_retrieval_node)
    workflow.add_node("rca_investigation", rca_investigation_node)
    workflow.add_node("evidence_verification", evidence_verification_node)

    # Define the order in which the nodes will run.
    workflow.add_edge(START, "log_analysis")
    workflow.add_edge("log_analysis", "runbook_retrieval")
    workflow.add_edge("runbook_retrieval", "rca_investigation")
    workflow.add_edge("rca_investigation", "evidence_verification")

    # Choose the route after evidence verification.
    workflow.add_conditional_edges(
            "evidence_verification",
            route_after_verification,
            {
                "complete": END,
                "incomplete": END,
            },
        )
    
    # Compile the workflow so it can be executed.
    return workflow.compile()

