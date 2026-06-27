import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import PostmortemAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
AGENT_ID:postmortem_agent

You are PostmortemAgent in OpsPilot.

Task:
Create a concise incident postmortem report.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "postmortem_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "confidence" must be a number between 0 and 1.
- "incident_title" must be a string.
- "impact_summary" must be a string.
- "root_cause_summary" must be a string.
- "timeline_summary" must be an array of strings.
- "actions_taken" must be an array of strings.
- "what_worked" must be an array of strings.
- "what_failed_or_was_missing" must be an array of strings.
- "follow_up_items" must be an array of objects with:
  "title" (string), "priority" (one of: "low", "medium", "high"),
  "owner_role" (string).
- If evidence is limited, use:
  status="insufficient_evidence",
  and explain which evidence is missing.

Return JSON with exactly these keys:
{
  "agent_name": "postmortem_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "incident_title": "string",
  "impact_summary": "string",
  "root_cause_summary": "string",
  "timeline_summary": ["string"],
  "actions_taken": ["string"],
  "what_worked": ["string"],
  "what_failed_or_was_missing": ["string"],
  "follow_up_items": [
    {
      "title": "string",
      "priority": "high",
      "owner_role": "string"
    }
  ]
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for PostmortemAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "postmortem_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "confidence" is a number between 0 and 1.
- Ensure "priority" in follow_up_items is one of: "low", "medium", "high".
- Ensure arrays are arrays of strings or objects as required.
"""


def _mask_secrets(value: Any) -> Any:
    if isinstance(value, dict):
        masked: dict[str, Any] = {}
        for key, item in value.items():
            lower_key = key.lower()
            if any(token in lower_key for token in ("key", "token", "secret", "password", "authorization")):
                masked[key] = "***MASKED***"
            else:
                masked[key] = _mask_secrets(item)
        return masked

    if isinstance(value, list):
        return [_mask_secrets(item) for item in value]

    if isinstance(value, str) and value.startswith("sk-"):
        return "sk-***MASKED***"

    return value


def _validation_error_details(error: ValidationError) -> list[dict[str, Any]]:
    details: list[dict[str, Any]] = []
    for item in error.errors():
        details.append(
            {
                "location": list(item.get("loc", ())),
                "message": item.get("msg", "validation error"),
                "type": item.get("type", "unknown"),
            }
        )
    return details


class PostmortemAgent(BaseAgent):
    name = "postmortem_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> PostmortemAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("PostmortemAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return PostmortemAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("PostmortemAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("PostmortemAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return PostmortemAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("PostmortemAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> PostmortemAgentOutput:
        return PostmortemAgentOutput(
            agent_name="postmortem_agent",
            status="failed",
            confidence=0.0,
            summary="Postmortem agent could not validate the model response and returned a safe fallback result.",
            incident_title="Postmortem could not be generated",
            impact_summary="Model output could not be validated.",
            root_cause_summary="Unknown — model output could not be validated.",
            timeline_summary=["Review raw postmortem model output in logs."],
            actions_taken=[],
            what_worked=[],
            what_failed_or_was_missing=["Model output could not be validated."],
            follow_up_items=[{"title": "Review postmortem model output", "priority": "high", "owner_role": "sre"}],
        )
