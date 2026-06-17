import asyncio
import json
from datetime import datetime, timezone
from itertools import count
from typing import Any, Dict, Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.api.routes.api_incidents import SyntheticIncident, append_timeline_event, store_incident

router = APIRouter(prefix="/api/alerts", tags=["alerts"])

AlertSeverity = Literal["P0", "P1", "P2", "P3"]

alert_sequence = count(1)
alert_store: list[dict[str, Any]] = []

alert_templates = [
    {
        "service": "checkout-api",
        "severity": "P1",
        "message": "Checkout p95 latency exceeded threshold",
        "signal": "p95 latency 2.8s",
        "region": "eu-central-1",
        "type": "latency",
        "affected_users": 12600,
    },
    {
        "service": "auth-service",
        "severity": "P0",
        "message": "Authentication success rate dropped below 70%",
        "signal": "auth success rate 68%",
        "region": "us-east-1",
        "type": "outage",
        "affected_users": 41200,
    },
    {
        "service": "cache-layer",
        "severity": "P2",
        "message": "Cache hit ratio degraded for checkout path",
        "signal": "cache hit ratio 41%",
        "region": "eu-west-1",
        "type": "resource",
        "affected_users": 7200,
    },
    {
        "service": "notification-svc",
        "severity": "P3",
        "message": "Delivery queue age above baseline",
        "signal": "queue age 7m",
        "region": "us-west-2",
        "type": "queue",
        "affected_users": 850,
    },
]


class AlertEvent(BaseModel):
    id: str
    timestamp: str
    service: str
    severity: AlertSeverity
    message: str
    signal: str
    region: str
    type: str
    affected_users: int


def reset_alert_state() -> None:
    alert_store.clear()


def create_alert() -> dict[str, Any]:
    sequence = next(alert_sequence)
    template = alert_templates[(sequence - 1) % len(alert_templates)]
    alert = {
        "id": f"ALT-{1000 + sequence}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **template,
    }
    alert_store.insert(0, alert)
    del alert_store[25:]
    return alert


def alert_to_incident(alert: dict[str, Any]) -> SyntheticIncident:
    return SyntheticIncident(
        id=alert["id"].replace("ALT", "INC"),
        timestamp=alert["timestamp"],
        service=alert["service"],
        severity=alert["severity"],
        state="open",
        message=alert["message"],
        recommended_action="Investigate correlated metrics, logs, and recent changes",
        type=alert["type"],
        assignee="unassigned",
        affected_users=alert["affected_users"],
        region=alert["region"],
        tags=[alert["type"], alert["service"]],
        ai_confidence=76,
        mttr_minutes=None,
    )


@router.get("")
async def list_alerts():
    while len(alert_store) < len(alert_templates):
        create_alert()
    return {"alerts": alert_store}


@router.post("/{alert_id}/incident")
async def create_incident_from_alert(alert_id: str):
    alert = next((item for item in alert_store if item["id"] == alert_id), None)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    incident = store_incident(alert_to_incident(alert))
    append_timeline_event(
        incident["id"],
        "incident_created_from_alert",
        f"Incident created from live alert {alert_id}",
        metadata={"alert_id": alert_id},
    )
    return incident


@router.get("/stream")
async def stream_alerts():
    async def events():
        while True:
            alert = create_alert()
            yield f"event: alert\ndata: {json.dumps(alert)}\n\n"
            await asyncio.sleep(5)

    return StreamingResponse(events(), media_type="text/event-stream")
