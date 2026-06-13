from fastapi import APIRouter, HTTPException

from app.schemas.incidents import CreateIncidentRequest
from app.services.incident_service import orchestrator

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("")
async def create_incident(request: CreateIncidentRequest):
    state = await orchestrator.create_incident(request.alert.model_dump())
    return {
        "incident_id": state["incident_id"],
        "status": state["status"],
        "state": state
    }


@router.get("")
async def list_incidents():
    return orchestrator.list_incidents()


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    try:
        return orchestrator.get_incident(incident_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")


@router.post("/{incident_id}/approve")
async def approve_incident(incident_id: str):
    try:
        return await orchestrator.approve_and_execute(incident_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")
