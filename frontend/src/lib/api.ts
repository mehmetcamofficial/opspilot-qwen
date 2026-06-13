const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://127.0.0.1:8000";

export const demoAlertPayload = {
  alert: {
    name: "checkout_api_latency_high",
    description: "Checkout p95 latency exceeded threshold after recent cache configuration change.",
    service: "checkout-api",
    environment: "prod",
    triggered_at: "2026-07-10T00:00:00Z",
    labels: {
      team: "payments",
      region: "eu-central",
      severity_hint: "high"
    },
    observed_signals: [
      "checkout latency spike",
      "cache hit ratio drop",
      "db latency increase",
      "recent config deployment"
    ]
  }
};

export async function healthcheck() {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) throw new Error("Backend healthcheck failed");
  return res.json();
}

export async function createIncident() {
  const res = await fetch(`${API_BASE_URL}/incidents`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(demoAlertPayload)
  });

  if (!res.ok) throw new Error("Failed to create incident");
  return res.json();
}

export async function listIncidents() {
  const res = await fetch(`${API_BASE_URL}/incidents`);
  if (!res.ok) throw new Error("Failed to list incidents");
  return res.json();
}

export async function approveIncident(incidentId: string) {
  const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/approve`, {
    method: "POST"
  });

  if (!res.ok) throw new Error("Failed to approve incident");
  return res.json();
}
