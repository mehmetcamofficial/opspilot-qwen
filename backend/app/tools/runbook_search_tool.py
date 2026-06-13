async def search_runbooks(service: str, environment: str, symptoms: list[str]) -> dict:
    return {
        "retrieved_documents": [
            {
                "doc_id": "rb-017",
                "doc_type": "runbook",
                "title": "Checkout API Latency After Cache Regression",
                "service": service,
                "environment": environment,
                "similarity_score": 0.94,
                "content_excerpt": "Compare current cache config to last known good version and rollback if hit ratio collapses."
            },
            {
                "doc_id": "pi-044",
                "doc_type": "prior_incident",
                "title": "Cache TTL Misconfiguration Caused DB Fallback Storm",
                "service": service,
                "environment": environment,
                "similarity_score": 0.89,
                "content_excerpt": "Cache hit ratio collapse triggered DB fallback; rollback restored stability."
            }
        ]
    }
