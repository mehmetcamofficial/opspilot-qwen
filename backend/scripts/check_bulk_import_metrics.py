import json
from collections import Counter
from pathlib import Path

from fastapi.testclient import TestClient

from app.api.routes.api_incidents import reset_incident_state
from app.main import app


fixture_path = Path(__file__).parents[1] / "tests" / "fixtures" / "synthetic_incidents.json"
fixture = json.loads(fixture_path.read_text())
incidents = fixture["incidents"]


def expected_metrics():
    severity_counts = Counter(incident["severity"] for incident in incidents)
    state_counts = Counter(incident["state"] for incident in incidents)
    mttr_values = [
        incident["mttr_minutes"]
        for incident in incidents
        if isinstance(incident.get("mttr_minutes"), int)
    ]

    return {
        "total": fixture["count"],
        "by_severity": {severity: severity_counts.get(severity, 0) for severity in ["P0", "P1", "P2", "P3"]},
        "by_state": {state: state_counts.get(state, 0) for state in ["open", "investigating", "mitigating", "resolved"]},
        "active": fixture["count"] - state_counts["resolved"],
        "resolved": state_counts["resolved"],
        "affected_users": sum(incident["affected_users"] for incident in incidents),
        "average_mttr_minutes": round(sum(mttr_values) / len(mttr_values), 2),
    }


def main():
    reset_incident_state()
    client = TestClient(app)

    import_response = client.post("/api/incidents/bulk-import", json=fixture)
    import_response.raise_for_status()

    metrics_response = client.get("/api/incidents/metrics")
    metrics_response.raise_for_status()
    actual = metrics_response.json()
    expected = expected_metrics()

    if actual != expected:
        raise SystemExit(
            "Bulk import metrics mismatch\n"
            f"Expected: {json.dumps(expected, indent=2)}\n"
            f"Actual: {json.dumps(actual, indent=2)}"
        )

    print("Bulk import dashboard metrics verified.")
    print(json.dumps(actual, indent=2))


if __name__ == "__main__":
    main()
