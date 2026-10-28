
# Import the workflow builder.
from app.services.investigation_workflow import (
    build_investigation_workflow,
)

# Import the evidence verification node.
from app.services.investigation_workflow import evidence_verification_node


# Create sample incident data for testing.
initial_state = {
    "incident_title": "Database Connection Failure",
    "log_text": (
        "ERROR: Database connection timeout\n"
        "ERROR: Database authentication failed\n"
        "WARNING: Database response is slow"
    ),
    "log_analysis": {},
    "runbook_results": [],
    "root_cause": "",
    "evidence": [],
    "evidence_sufficient": False,
    "investigation_status": "started",
}


# Build the LangGraph workflow.
app = build_investigation_workflow()

# Run all nodes using the initial state.
final_state = app.invoke(initial_state)


# Display the final investigation results.
print("\n--- Investigation Results ---")
print("Incident:", final_state["incident_title"])
print("Severity:", final_state["log_analysis"]["severity"])
print("Error count:", final_state["log_analysis"]["error_count"])
print("Runbooks found:", len(final_state["runbook_results"]))
print("Possible root cause:", final_state["root_cause"])
print("Evidence:", final_state["evidence"])
print("Evidence sufficient:", final_state["evidence_sufficient"])
print("Investigation status:", final_state["investigation_status"])


# Check that every stage returned its expected data.
assert final_state["log_analysis"]["error_count"] == 2
assert len(final_state["runbook_results"]) > 0
assert final_state["root_cause"]
assert final_state["evidence"]


# Check whether the final status matches the evidence result.
if final_state["evidence_sufficient"]:
    assert final_state["investigation_status"] == "completed"
    print("Routing test passed: Investigation completed.")
else:
    assert final_state["investigation_status"] == "incomplete"
    print("Routing test passed: Investigation incomplete.")

print("Conditional routing test passed!")


print("\nAll workflow tests passed!")


# Create a test case with no supporting evidence.
incomplete_state = {
    "root_cause": "Possible root cause could not be identified.",
    "evidence": [],
}


# Check the evidence.
verification_result = evidence_verification_node(incomplete_state)

# Confirm that the investigation is marked as incomplete.
assert verification_result["evidence_sufficient"] is False
assert verification_result["investigation_status"] == "incomplete"

print("Evidence verification test passed!")
print("Investigation correctly marked as incomplete.")
