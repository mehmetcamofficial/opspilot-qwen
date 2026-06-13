async def get_metrics(service: str, environment: str, time_window_minutes: int = 30) -> dict:
    return {
        "series": [
            {"metric_name": "checkout_p95_latency_ms", "baseline": 420, "current": 1820, "trend": "up", "unit": "ms"},
            {"metric_name": "cache_hit_ratio", "baseline": 0.91, "current": 0.24, "trend": "down", "unit": "ratio"},
            {"metric_name": "db_query_latency_ms", "baseline": 38, "current": 210, "trend": "up", "unit": "ms"}
        ]
    }
