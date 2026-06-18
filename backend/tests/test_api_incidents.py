import json
from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes.alerts import reset_alert_state
from app.api.routes.api_incidents import reset_incident_state
from app.main import app


client = TestClient(app)
fixture_path = Path(__file__).parent / "fixtures" / "synthetic_incidents.json"
fixture = json.loads(fixture_path.read_text())
incidents = fixture["incidents"]


def setup_function():
    reset_alert_state()
    reset_incident_state()


def incident_for_severity(severity):
    return next(incident for incident in incidents if incident["severity"] == severity)


def test_api_incidents_accepts_each_severity_level():
    for severity in ["P0", "P1", "P2", "P3"]:
        response = client.post("/api/incidents", json=incident_for_severity(severity))

        assert response.status_code == 200
        body = response.json()
        assert body["severity"] == severity
        assert body["id"] == incident_for_severity(severity)["id"]


def test_incident_state_machine_allows_open_to_investigating_to_resolved():
    incident = {
        **incident_for_severity("P1"),
        "id": "INC-STATE-MACHINE",
        "state": "open",
    }
    create_response = client.post("/api/incidents", json=incident)

    assert create_response.status_code == 200
    assert create_response.json()["state"] == "open"

    investigating_response = client.post(
        "/api/incidents/INC-STATE-MACHINE/transition",
        json={"state": "investigating"},
    )

    assert investigating_response.status_code == 200
    assert investigating_response.json()["state"] == "investigating"

    resolved_response = client.post(
        "/api/incidents/INC-STATE-MACHINE/transition",
        json={"state": "resolved"},
    )

    assert resolved_response.status_code == 200
    body = resolved_response.json()
    assert body["state"] == "resolved"
    assert body["state_history"][-2]["from"] == "open"
    assert body["state_history"][-2]["to"] == "investigating"
    assert body["state_history"][-1]["from"] == "investigating"
    assert body["state_history"][-1]["to"] == "resolved"

    timeline_response = client.get("/api/incidents/INC-STATE-MACHINE/timeline")
    timeline_events = [item["event"] for item in timeline_response.json()["timeline"]]
    assert timeline_response.status_code == 200
    assert timeline_events == ["incident_created", "state_changed", "state_changed"]


def test_incident_state_machine_rejects_open_to_resolved_jump():
    incident = {
        **incident_for_severity("P2"),
        "id": "INC-INVALID-TRANSITION",
        "state": "open",
    }
    client.post("/api/incidents", json=incident)

    response = client.post(
        "/api/incidents/INC-INVALID-TRANSITION/transition",
        json={"state": "resolved"},
    )

    assert response.status_code == 409
    assert "open -> resolved" in response.json()["detail"]


def test_p0_incident_triggers_notification_event():
    response = client.post("/api/incidents", json=incident_for_severity("P0"))

    assert response.status_code == 200

    notifications_response = client.get("/api/incidents/notifications")

    assert notifications_response.status_code == 200
    notifications = notifications_response.json()
    assert len(notifications) == 1
    assert notifications[0]["severity"] == "P0"
    assert notifications[0]["incident_id"] == incident_for_severity("P0")["id"]


def test_non_p0_incident_does_not_trigger_notification_event():
    response = client.post("/api/incidents", json=incident_for_severity("P1"))

    assert response.status_code == 200
    assert client.get("/api/incidents/notifications").json() == []


def test_bulk_import_calculates_dashboard_metrics_from_synthetic_incidents():
    response = client.post("/api/incidents/bulk-import", json=fixture)

    assert response.status_code == 200
    assert response.json()["imported"] == fixture["count"]

    metrics_response = client.get("/api/incidents/metrics")

    assert metrics_response.status_code == 200
    metrics = metrics_response.json()
    severity_counts = Counter(incident["severity"] for incident in incidents)
    state_counts = Counter(incident["state"] for incident in incidents)
    mttr_values = [
        incident["mttr_minutes"]
        for incident in incidents
        if isinstance(incident.get("mttr_minutes"), int)
    ]

    assert metrics["total"] == fixture["count"]
    assert metrics["by_severity"] == {severity: severity_counts.get(severity, 0) for severity in ["P0", "P1", "P2", "P3"]}
    assert metrics["by_state"] == {state: state_counts.get(state, 0) for state in ["open", "investigating", "mitigating", "resolved"]}
    assert metrics["active"] == fixture["count"] - state_counts["resolved"]
    assert metrics["resolved"] == state_counts["resolved"]
    assert metrics["affected_users"] == sum(incident["affected_users"] for incident in incidents)
    assert metrics["average_mttr_minutes"] == round(sum(mttr_values) / len(mttr_values), 2)


def test_alert_list_returns_live_operational_signal():
    response = client.get("/api/alerts")

    assert response.status_code == 200
    alerts = response.json()["alerts"]
    assert len(alerts) >= 1
    assert alerts[0]["id"].startswith("ALT-")
    assert alerts[0]["severity"] in ["P0", "P1", "P2", "P3"]


def test_alert_can_be_promoted_to_incident_and_p0_notifies():
    alerts = client.get("/api/alerts").json()["alerts"]
    p0_alert = next(alert for alert in alerts if alert["severity"] == "P0")

    response = client.post(f"/api/alerts/{p0_alert['id']}/incident")

    assert response.status_code == 200
    incident = response.json()
    assert incident["id"].startswith("INC-")
    assert incident["state"] == "open"
    assert incident["severity"] == "P0"

    notifications = client.get("/api/incidents/notifications").json()
    assert notifications[-1]["severity"] == "P0"
    assert notifications[-1]["incident_id"] == incident["id"]

    timeline = client.get(f"/api/incidents/{incident['id']}/timeline").json()["timeline"]
    timeline_events = [item["event"] for item in timeline]
    assert "incident_created" in timeline_events
    assert "notification_sent" in timeline_events
    assert "incident_created_from_alert" in timeline_events


def test_incident_timeline_accepts_operator_event():
    incident = {
        **incident_for_severity("P2"),
        "id": "INC-TIMELINE",
        "state": "open",
    }
    client.post("/api/incidents", json=incident)

    response = client.post(
        "/api/incidents/INC-TIMELINE/timeline",
        json={
            "event": "operator_note",
            "message": "Responder confirmed customer-facing degradation.",
            "actor": "responder",
        },
    )

    assert response.status_code == 200
    assert response.json()["event"] == "operator_note"

    timeline = client.get("/api/incidents/INC-TIMELINE/timeline").json()["timeline"]
    assert timeline[-1]["actor"] == "responder"
    assert timeline[-1]["message"] == "Responder confirmed customer-facing degradation."


def test_incident_assignment_updates_owner_and_timeline():
    incident = {
        **incident_for_severity("P1"),
        "id": "INC-ASSIGN",
        "state": "open",
        "assignee": "unassigned",
    }
    client.post("/api/incidents", json=incident)

    response = client.post(
        "/api/incidents/INC-ASSIGN/assign",
        json={"assignee": "sre-primary", "actor": "commander"},
    )

    assert response.status_code == 200
    assert response.json()["assignee"] == "sre-primary"

    timeline = client.get("/api/incidents/INC-ASSIGN/timeline").json()["timeline"]
    assert timeline[-1]["event"] == "assigned"
    assert timeline[-1]["actor"] == "commander"
    assert timeline[-1]["metadata"]["previous_assignee"] == "unassigned"
    assert timeline[-1]["metadata"]["assignee"] == "sre-primary"


def test_public_status_is_operational_without_active_incidents():
    response = client.get("/api/incidents/public-status")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "operational"
    assert body["active_incidents"] == 0
    assert body["highest_severity"] is None
    assert body["services"] == []


def test_public_status_reports_active_p0_incident():
    incident = {
        **incident_for_severity("P0"),
        "id": "INC-PUBLIC-P0",
        "state": "open",
        "assignee": "sre-primary",
    }
    client.post("/api/incidents", json=incident)

    response = client.get("/api/incidents/public-status")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "major_outage"
    assert body["active_incidents"] == 1
    assert body["highest_severity"] == "P0"
    assert body["services"][0]["incident_id"] == "INC-PUBLIC-P0"
    assert body["services"][0]["assignee"] == "sre-primary"


def test_ai_insights_returns_ranked_recommendations_and_summary():
    base_incident = {
        **incident_for_severity("P1"),
        "id": "INC-AI-BASE",
        "service": "checkout-api",
        "tags": ["latency", "checkout-api"],
        "recommended_action": "Rollback cache configuration",
    }
    similar_incident = {
        **incident_for_severity("P2"),
        "id": "INC-AI-SIMILAR",
        "service": "checkout-api",
        "tags": ["latency", "checkout-api"],
        "recommended_action": "Restored previous cache TTL",
    }
    client.post("/api/incidents", json=similar_incident)
    client.post("/api/incidents", json=base_incident)

    response = client.get("/api/incidents/INC-AI-BASE/ai-insights")

    assert response.status_code == 200
    body = response.json()
    assert body["incident_id"] == "INC-AI-BASE"
    assert len(body["root_causes"]) == 3
    assert body["root_causes"][0]["confidence"] >= body["root_causes"][1]["confidence"]
    assert body["similar_incidents"][0]["incident_id"] == "INC-AI-SIMILAR"
    assert body["triage"]["suggested_assignee"] == "payments-sre"
    assert body["safety_check"]["requires_confirmation"] is True
    assert body["anomaly"]["detected"] is True
    assert "checkout-api" in body["summary"]


def test_public_status_hides_resolved_incidents():
    incident = {
        **incident_for_severity("P1"),
        "id": "INC-PUBLIC-RESOLVED",
        "state": "resolved",
    }
    client.post("/api/incidents", json=incident)

    response = client.get("/api/incidents/public-status")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "operational"
    assert body["active_incidents"] == 0
    assert body["services"] == []
