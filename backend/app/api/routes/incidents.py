from fastapi import APIRouter
from app.schemas.incidents import CreateIncidentRequest

router = APIRouter(prefix="/incidents", tags=["incidents"])


@router.post("")
async def create_incident(request: CreateIncidentRequest):
    return {
        "incident_id": "inc-demo-001",
        "status": "triaging",
        "state": {
            "alert": request.alert.model_dump(),
            "message": "Incident accepted. Agent orchestration will be added next."
        }
    }


@router.get("")
async def list_incidents():
    return [
        {
            "incident_id": "inc-demo-001",
            "status": "triaging",
            "service": "checkout-api"
        }
    ]
