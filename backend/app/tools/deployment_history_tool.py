async def get_deployment_history(service: str, environment: str) -> dict:
    return {
        "events": [
            {
                "timestamp": "2026-07-09T23:56:00Z",
                "type": "config_change",
                "service": service,
                "description": "Updated cache TTL and namespace routing config"
            }
        ]
    }
