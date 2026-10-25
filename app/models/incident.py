
from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    title: str = Field(
        min_length=3,
        max_length=150,
        description="Short incident title",
    )

    description: str = Field(
        min_length=5,
        description="Description of the incident",
    )

    severity: str = Field(
        default="medium",
        description="Incident severity: low, medium, or high",
    )

    log_text: str = Field(
        min_length=1,
        description="Application logs related to the incident",
    )
