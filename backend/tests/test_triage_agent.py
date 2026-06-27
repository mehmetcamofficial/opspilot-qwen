import asyncio

from app.agents.triage_agent import TriageAgent


class FakeQwenClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def generate_json(self, system_prompt, user_payload):
        self.calls.append({"system_prompt": system_prompt, "user_payload": user_payload})
        return self.responses.pop(0)


def triage_payload():
    return {
        "incident_id": "inc-test-1234",
        "alert": {
            "name": "checkout_api_latency_high",
            "description": "Checkout p95 latency exceeded threshold after recent cache configuration change.",
            "service": "checkout-api",
            "environment": "prod",
            "triggered_at": "2026-07-10T00:00:00Z",
            "labels": {
                "team": "payments",
                "region": "eu-central",
                "severity_hint": "high",
            },
            "observed_signals": [
                "checkout latency spike",
                "cache hit ratio drop",
                "db latency increase",
                "recent config deployment",
            ],
        },
    }


def valid_triage_response():
    return {
        "agent_name": "triage_agent",
        "status": "success",
        "confidence": 0.83,
        "summary": "High-severity checkout latency incident with likely customer impact.",
        "incident_type": "latency",
        "severity": "high",
        "business_impact": "Customers may experience slow or failed checkout attempts.",
        "impacted_services": ["checkout-api", "cache", "orders-db"],
        "blast_radius": "customer_visible",
        "initial_hypotheses": [
            {
                "title": "Deployment-related cache regression",
                "confidence": 0.71,
                "reason": "Latency spike coincides with cache degradation and a recent configuration change.",
            }
        ],
        "recommended_next_steps": [
            "Inspect checkout latency metrics.",
            "Review recent cache configuration changes.",
        ],
        "recommended_tools": [
            "metrics_tool",
            "logs_tool",
            "deployment_history_tool",
            "runbook_search_tool",
        ],
        "handoff_agents": [
            "observability_agent",
            "runbook_agent",
            "hypothesis_agent",
        ],
    }


def invalid_triage_response():
    return {
        "status": "investigating",
        "summary": "Need more triage.",
    }


def test_triage_agent_repairs_invalid_llm_output_and_validates_successfully():
    client = FakeQwenClient([invalid_triage_response(), valid_triage_response()])
    agent = TriageAgent(client)

    result = asyncio.run(agent.run(triage_payload()))

    assert result.agent_name == "triage_agent"
    assert result.status == "success"
    assert result.incident_type == "latency"
    assert result.business_impact == "Customers may experience slow or failed checkout attempts."
    assert len(client.calls) == 2
    assert "failed schema validation" in client.calls[1]["system_prompt"]


def test_triage_agent_returns_graceful_failure_after_repair_validation_failure():
    client = FakeQwenClient([invalid_triage_response(), invalid_triage_response()])
    agent = TriageAgent(client)

    result = asyncio.run(agent.run(triage_payload()))

    assert result.agent_name == "triage_agent"
    assert result.status == "failed"
    assert result.incident_type == "unknown"
    assert result.blast_radius == "unknown"
    assert result.impacted_services == ["checkout-api"]
    assert result.recommended_tools == ["logs_tool"]
