from datetime import datetime, UTC


async def execute_action(action_id: str, title: str) -> dict:
    return {
        "action_id": action_id,
        "title": title,
        "status": "executed",
        "executed_at": datetime.now(UTC).isoformat()
    }
