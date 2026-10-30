from fastapi import APIRouter, HTTPException
from app.models.incident import IncidentRequest
from app.db.repository import (
    create_incident,
    get_all_incidents,
    get_incident_by_id,
    update_incident_status,
    get_audit_logs,
    create_audit_log
)
from app.services.log_analyzer import analyze_logs
import json
from app.core.redis_client import redis_client


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
    cache_key = f"incident:{incident_id}"

    try:
        # Step 1: Check Redis cache
        cached_incident = redis_client.get(cache_key)

        if cached_incident:
            return {
                "source": "redis_cache",
                "incident": json.loads(cached_incident),
            }

        # Step 2: Fetch from PostgreSQL if cache misses
        incident = get_incident_by_id(incident_id)

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        # Step 3: Store incident in Redis for 5 minutes
        redis_client.setex(
            cache_key,
            300,
            json.dumps(incident, default=str),
        )

        return {
            "source": "postgresql",
            "incident": incident,
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve incident",
        )


@router.post("/")
def create_incident_endpoint(incident: IncidentRequest):
    try:
        log_analysis = analyze_logs(incident.log_text)

        incident_data = incident.model_dump()
        incident_data["severity"] = log_analysis["severity"]

        saved_incident = create_incident(incident_data)

        return {
            "message": "Incident saved successfully",
            "incident": saved_incident,
            "log_analysis": log_analysis,
        }

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to analyze logs or save incident",
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

    redis_client.delete(f"incident:{incident_id}")

    return {
        "message": "Incident status updated successfully",
        "incident": incident,
    }




@router.get("/{incident_id}/audit-logs")
def list_audit_logs(incident_id: int):
    try:
        # Check whether the incident exists
        incident = get_incident_by_id(incident_id)

        if incident is None:
            raise HTTPException(
                status_code=404,
                detail="Incident not found",
            )

        # Fetch audit history
        logs = get_audit_logs(incident_id)

        return {
            "incident_id": incident_id,
            "total": len(logs),
            "audit_logs": logs,
        }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to retrieve audit logs",
        )
