from fastapi import APIRouter, HTTPException
from app.models.incident import IncidentRequest
from app.db.repository import (
    create_incident,
    get_all_incidents,
    get_incident_by_id,
    update_incident_status,
)

router = APIRouter(prefix="/incidents", tags=["Incidents"])



@router.get("/")
def list_incidents():
    try:
        incidents = get_all_incidents()
        return {
            "total": len(incidents),
            "incidents": incidents,
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve incidents from database",
        )


@router.get("/{incident_id}")
def get_incident(incident_id: int):
    try:
        incident = get_incident_by_id(incident_id)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve incident from database",
        )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return incident


@router.post("/")
def create_incident_endpoint(incident: IncidentRequest):
    try:
        saved_incident = create_incident(incident.model_dump())
        return {
            "message": "Incident saved successfully",
            "incident": saved_incident,
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to save incident to database",
        )


@router.patch("/{incident_id}/status")
def update_status(incident_id: int, status: str):
    try:
        incident = update_incident_status(incident_id, status)
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to update incident status",
        )

    if incident is None:
        raise HTTPException(
            status_code=404,
            detail="Incident not found",
        )

    return {
        "message": "Incident status updated successfully",
        "incident": incident,
    }