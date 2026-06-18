from collections import Counter
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(prefix="/api/incidents", tags=["api-incidents"])

IncidentState = Literal["open", "investigating", "mitigating", "resolved"]
IncidentSeverity = Literal["P0", "P1", "P2", "P3"]

ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    "open": {"investigating"},
    "investigating": {"resolved", "mitigating"},
    "mitigating": {"resolved"},
    "resolved": set(),
}

incident_store: dict[str, dict[str, Any]] = {}
notification_events: list[dict[str, Any]] = []


class SyntheticIncident(BaseModel):
    id: str
    timestamp: str
    service: str
    severity: IncidentSeverity
    state: IncidentState
    message: str
    recommended_action: str
    type: str
    assignee: str
    affected_users: int
    region: str
    tags: List[str]
    ai_confidence: int
    mttr_minutes: Optional[int] = None


class StateTransitionRequest(BaseModel):
    state: IncidentState


class BulkImportRequest(BaseModel):
    incidents: List[SyntheticIncident]


class TimelineEventRequest(BaseModel):
    event: str
    message: str
    actor: str = "system"


class AssignIncidentRequest(BaseModel):
    assignee: str
    actor: str = "commander"


def reset_incident_state() -> None:
    incident_store.clear()
    notification_events.clear()


def append_timeline_event(
    incident_id: str,
    event: str,
    message: str,
    actor: str = "system",
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    incident = incident_store[incident_id]
    timeline_event = {
        "event": event,
        "message": message,
        "actor": actor,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metadata": metadata or {},
    }
    incident.setdefault("timeline", []).append(timeline_event)
    incident_store[incident_id] = incident
    return timeline_event


def record_p0_notification(incident: dict[str, Any]) -> None:
    if incident["severity"] != "P0":
        return

    notification_events.append(
        {
            "incident_id": incident["id"],
            "severity": incident["severity"],
            "service": incident["service"],
            "message": f"P0 incident received for {incident['service']}",
            "triggered_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    append_timeline_event(
        incident["id"],
        "notification_sent",
        f"P0 notification queued for {incident['service']}",
        metadata={"severity": incident["severity"], "service": incident["service"]},
    )


def store_incident(incident: SyntheticIncident) -> dict[str, Any]:
    stored = incident.model_dump()
    incident_store[incident.id] = stored
    append_timeline_event(
        incident.id,
        "incident_created",
        f"Incident opened for {incident.service}",
        metadata={"severity": incident.severity, "state": incident.state},
    )
    record_p0_notification(stored)
    return incident_store[incident.id]


def public_status_summary() -> dict[str, Any]:
    incidents = list(incident_store.values())
    active_incidents = [incident for incident in incidents if incident["state"] != "resolved"]
    highest_severity = next(
        (severity for severity in ["P0", "P1", "P2", "P3"] if any(incident["severity"] == severity for incident in active_incidents)),
        None,
    )
    platform_status = "operational"
    if highest_severity == "P0":
        platform_status = "major_outage"
    elif highest_severity in {"P1", "P2"}:
        platform_status = "degraded"

    services = []
    for incident in active_incidents:
        services.append(
            {
                "service": incident["service"],
                "status": "impacted" if incident["severity"] in {"P0", "P1"} else "degraded",
                "severity": incident["severity"],
                "incident_id": incident["id"],
                "message": incident["message"],
                "assignee": incident.get("assignee", "unassigned"),
            }
        )

    return {
        "status": platform_status,
        "active_incidents": len(active_incidents),
        "highest_severity": highest_severity,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "services": services,
    }


def similar_incidents_for(incident: dict[str, Any]) -> list[dict[str, Any]]:
    candidates = []
    incident_tags = set(incident.get("tags", []))
    for candidate in incident_store.values():
        if candidate["id"] == incident["id"]:
            continue
        shared_tags = incident_tags.intersection(candidate.get("tags", []))
        if candidate["service"] == incident["service"] or shared_tags:
            candidates.append(
                {
                    "incident_id": candidate["id"],
                    "service": candidate["service"],
                    "severity": candidate["severity"],
                    "resolution": candidate.get("recommended_action", "Review prior mitigation notes"),
                    "similarity": min(0.98, 0.62 + (0.18 if candidate["service"] == incident["service"] else 0) + (0.05 * len(shared_tags))),
                }
            )

    return sorted(candidates, key=lambda item: item["similarity"], reverse=True)[:3]


def ai_insights_for(incident: dict[str, Any]) -> dict[str, Any]:
    service = incident["service"]
    severity = incident["severity"]
    affected_users = incident.get("affected_users", 0)
    signal_type = incident.get("type", "latency")
    confidence = incident.get("ai_confidence", 76)
    timeline = incident.get("timeline", [])
    is_stalling = incident["state"] != "resolved" and len(timeline) >= 3
    suggested_assignee = "sre-primary" if severity in {"P0", "P1"} else "platform-responder"
    if service in {"checkout-api", "payment-api"}:
        suggested_assignee = "payments-sre"
    elif service in {"auth-service"}:
        suggested_assignee = "identity-sre"

    root_causes = [
        {
            "title": f"{service} regression after recent operational change",
            "confidence": min(0.96, confidence / 100),
            "evidence": ["recent deployment/config signal", incident["message"], incident.get("recommended_action", "Investigate correlated telemetry")],
        },
        {
            "title": f"{signal_type} saturation affecting downstream dependencies",
            "confidence": 0.73 if severity in {"P0", "P1"} else 0.62,
            "evidence": [f"{affected_users} affected users", f"severity {severity}", f"region {incident.get('region', 'unknown')}"],
        },
        {
            "title": "Noisy alert without customer-wide impact",
            "confidence": 0.31 if severity in {"P0", "P1"} else 0.48,
            "evidence": ["requires responder confirmation", "compare against baseline metrics"],
        },
    ]

    return {
        "incident_id": incident["id"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "root_causes": root_causes,
        "similar_incidents": similar_incidents_for(incident),
        "triage": {
            "severity": severity,
            "suggested_assignee": suggested_assignee,
            "reason": f"{service} has {affected_users} affected users and severity {severity}.",
        },
        "escalation": {
            "should_escalate": severity == "P0" or is_stalling,
            "reason": "P0 severity requires immediate commander escalation." if severity == "P0" else ("Incident has multiple timeline events without resolution." if is_stalling else "No escalation required yet."),
        },
        "safety_check": {
            "risk_level": "high" if severity == "P0" else "medium",
            "requires_confirmation": True,
            "explanation": "Review blast radius, rollback safety, and evidence confidence before executing remediation.",
        },
        "anomaly": {
            "detected": severity in {"P0", "P1", "P2"},
            "baseline": "normal operating threshold",
            "current": incident.get("message", "current signal exceeds expected baseline"),
            "deviation": "critical" if severity == "P0" else ("elevated" if severity in {"P1", "P2"} else "low"),
        },
        "summary": f"{severity} incident on {service}: {incident['message']} Recommended owner is {suggested_assignee}; safest next step is to validate evidence and confirm remediation.",
    }


async def parse_bulk_payload(request: Request) -> BulkImportRequest:
    payload = await request.json()
    if isinstance(payload, list):
        return BulkImportRequest(incidents=payload)
    if isinstance(payload, dict) and "incidents" in payload:
        return BulkImportRequest.model_validate(payload)
    raise HTTPException(status_code=422, detail="Expected an incident array or an object with incidents.")


@router.post("")
async def create_incident(incident: SyntheticIncident):
    return store_incident(incident)


@router.get("")
async def list_incidents():
    return list(incident_store.values())


@router.get("/notifications")
async def list_notifications():
    return notification_events


@router.get("/public-status")
async def get_public_status():
    return public_status_summary()


@router.get("/{incident_id}/timeline")
async def get_incident_timeline(incident_id: str):
    try:
        incident = incident_store[incident_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")
    return {"incident_id": incident_id, "timeline": incident.get("timeline", [])}


@router.post("/{incident_id}/timeline")
async def add_incident_timeline_event(incident_id: str, timeline_event: TimelineEventRequest):
    try:
        event = append_timeline_event(
            incident_id,
            timeline_event.event,
            timeline_event.message,
            actor=timeline_event.actor,
        )
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")
    return event


@router.post("/{incident_id}/assign")
async def assign_incident(incident_id: str, assignment: AssignIncidentRequest):
    try:
        incident = incident_store[incident_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")

    previous_assignee = incident.get("assignee", "unassigned")
    incident["assignee"] = assignment.assignee
    incident_store[incident_id] = incident
    append_timeline_event(
        incident_id,
        "assigned",
        f"Incident assigned to {assignment.assignee}",
        actor=assignment.actor,
        metadata={"previous_assignee": previous_assignee, "assignee": assignment.assignee},
    )
    return incident_store[incident_id]


@router.post("/bulk-import")
async def bulk_import(request: Request):
    payload = await parse_bulk_payload(request)
    imported = [store_incident(incident) for incident in payload.incidents]
    return {
        "imported": len(imported),
        "p0_notifications": len([event for event in notification_events if event["severity"] == "P0"]),
        "incidents": imported,
    }


@router.get("/metrics")
async def incident_metrics():
    incidents = list(incident_store.values())
    severity_counts = Counter(incident["severity"] for incident in incidents)
    state_counts = Counter(incident["state"] for incident in incidents)
    mttr_values = [
        incident["mttr_minutes"]
        for incident in incidents
        if isinstance(incident.get("mttr_minutes"), int)
    ]

    return {
        "total": len(incidents),
        "by_severity": {severity: severity_counts.get(severity, 0) for severity in ["P0", "P1", "P2", "P3"]},
        "by_state": {state: state_counts.get(state, 0) for state in ["open", "investigating", "mitigating", "resolved"]},
        "active": len([incident for incident in incidents if incident["state"] != "resolved"]),
        "resolved": state_counts.get("resolved", 0),
        "affected_users": sum(incident["affected_users"] for incident in incidents),
        "average_mttr_minutes": round(sum(mttr_values) / len(mttr_values), 2) if mttr_values else None,
    }


@router.get("/{incident_id}/ai-insights")
async def get_incident_ai_insights(incident_id: str):
    try:
        incident = incident_store[incident_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")
    return ai_insights_for(incident)


@router.get("/{incident_id}")
async def get_incident(incident_id: str):
    try:
        return incident_store[incident_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")


@router.post("/{incident_id}/transition")
async def transition_incident(incident_id: str, transition: StateTransitionRequest):
    try:
        incident = incident_store[incident_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")

    current_state = incident["state"]
    next_state = transition.state
    if next_state not in ALLOWED_TRANSITIONS[current_state]:
        raise HTTPException(
            status_code=409,
            detail=f"Invalid state transition: {current_state} -> {next_state}",
        )

    incident["state"] = next_state
    incident.setdefault("state_history", []).append(
        {
            "from": current_state,
            "to": next_state,
            "transitioned_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    incident_store[incident_id] = incident
    append_timeline_event(
        incident_id,
        "state_changed",
        f"Incident moved from {current_state} to {next_state}",
        metadata={"from": current_state, "to": next_state},
    )
    return incident
