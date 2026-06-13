from typing import Dict, List, Optional
from pydantic import BaseModel


class AlertLabels(BaseModel):
    team: Optional[str] = None
    region: Optional[str] = None
    severity_hint: Optional[str] = None


class AlertPayload(BaseModel):
    name: str
    description: str
    service: str
    environment: str
    triggered_at: str
    labels: AlertLabels = AlertLabels()
    observed_signals: List[str] = []


class CreateIncidentRequest(BaseModel):
    alert: AlertPayload


class IncidentStateResponse(BaseModel):
    incident_id: str
    status: str
    state: Dict
