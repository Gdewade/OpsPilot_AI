from fastapi import APIRouter, HTTPException

from app.models.approval import ApprovalRequest, ApprovalDecision

from app.db.repository import (
    create_approval_request,
    get_approval_request,
    update_approval_decision,
    create_audit_log,
    get_incident_by_id,
)

router = APIRouter(prefix="/approvals", tags=["Human Approval"])


# Create a new approval request
@router.post("/")
def request_approval(data: ApprovalRequest):
    try:
        incident = get_incident_by_id(data.incident_id)

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        approval = create_approval_request(data.model_dump())

        return {
            "message": "Approval request created successfully",
            "approval": approval,
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to create approval request",
        )


# Get approval request by ID
@router.get("/{approval_id}")
def get_approval(approval_id: int):
    approval = get_approval_request(approval_id)

    if approval is None:
        raise HTTPException(
            status_code=404,
            detail="Approval request not found",
        )

    return approval


# Approve or reject a remediation action
@router.patch("/{approval_id}/decision")
def review_approval(approval_id: int, data: ApprovalDecision):
    try:
        approval = update_approval_decision(
            approval_id=approval_id,
            decision=data.decision,
            reviewed_by=data.reviewed_by,
            comments=data.comments,
        )

        if approval is None:
            raise HTTPException(
                status_code=404,
                detail="Approval request not found or already reviewed",
            )

        create_audit_log(
            incident_id=approval["incident_id"],
            action=f"REMEDIATION_{data.decision.upper()}",
            performed_by=data.reviewed_by,
            details=data.comments or data.action if False else (
                f"Approval request {approval_id}: {data.decision}"
            ),
        )

        return {
            "message": f"Remediation {data.decision} successfully",
            "approval": approval,
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to review approval request",
        )