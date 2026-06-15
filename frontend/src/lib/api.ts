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

async function fetchJson(url: string, options?: RequestInit) {
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      const body = await res.text();
      const message = body ? `${res.status} ${res.statusText}: ${body}` : `${res.status} ${res.statusText}`;
      throw new Error(message);
    }
    return res.json();
  } catch (error: unknown) {
    if (error instanceof Error) {
      throw new Error(`Backend request failed: ${error.message}`);
    }
    throw new Error("Backend request failed due to an unknown error.");
  }
}

export async function healthcheck() {
  return fetchJson(`${API_BASE_URL}/health`);
}

export async function createIncident() {
  return fetchJson(`${API_BASE_URL}/incidents`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(demoAlertPayload)
  });
}

export async function listIncidents() {
  return fetchJson(`${API_BASE_URL}/incidents`);
}

export async function approveIncident(incidentId: string) {
  return fetchJson(`${API_BASE_URL}/incidents/${incidentId}/approve`, {
    method: "POST"
  });
}
