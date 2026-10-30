from pydantic import BaseModel,Field
from typing import Literal


class ApprovalRequest(BaseModel):

    incident_id: int = Field(gt=0)

    action: str = Field(
        min_length=3,
        description="Proposed remediation action"
    )

    requested_by: str = Field(
        min_length=2,
        description="Person requesting approval"
    )


class ApprovalDecision(BaseModel):
    
    decision: Literal["approved", "rejected"]
    reviewed_by: str = Field(min_length=2)
    comments: str | None = None

