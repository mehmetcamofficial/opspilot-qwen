async def get_logs(service: str, environment: str, time_window_minutes: int = 30) -> dict:
    return {
        "top_patterns": [
            {"pattern": "cache_miss_fallback=db", "count": 1842, "severity": "warn"},
            {"pattern": "config_version=2026.07.10-rc3", "count": 1260, "severity": "info"}
        ]
    }
