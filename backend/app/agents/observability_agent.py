import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import ObservabilityAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
AGENT_ID:observability_agent

You are ObservabilityAgent in OpsPilot.

Task:
Analyze metrics, logs, and deployment history for incident evidence.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "observability_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "confidence" must be a number between 0 and 1.
- "metric_anomalies" must be an array of objects with:
  "metric_name" (string), "baseline" (number), "current" (number),
  "direction" (one of: "up", "down"),
  "severity" (one of: "low", "medium", "high"),
  "interpretation" (string).
- "log_findings" must be an array of objects with:
  "pattern" (string), "count" (integer),
  "severity" (one of: "info", "warn", "error"),
  "interpretation" (string).
- "deployment_findings" must be an array of objects with:
  "timestamp" (string), "event_type" (one of: "deploy", "config_change", "rollback"),
  "relevance" (one of: "high", "medium", "low"),
  "reason" (string).
- "suspected_subsystems" must be an array of objects with:
  "name" (string), "confidence" (number between 0 and 1), "reason" (string).
- "evidence_strength" must be exactly one of: "weak", "moderate", "strong".
- "open_questions" must be an array of strings.
- If evidence is limited, use:
  status="insufficient_evidence",
  evidence_strength="weak",
  and empty arrays where needed.

Return JSON with exactly these keys:
{
  "agent_name": "observability_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "metric_anomalies": [
    {
      "metric_name": "string",
      "baseline": 0.0,
      "current": 0.0,
      "direction": "up",
      "severity": "high",
      "interpretation": "string"
    }
  ],
  "log_findings": [
    {
      "pattern": "string",
      "count": 0,
      "severity": "warn",
      "interpretation": "string"
    }
  ],
  "deployment_findings": [
    {
      "timestamp": "string",
      "event_type": "config_change",
      "relevance": "high",
      "reason": "string"
    }
  ],
  "suspected_subsystems": [
    {
      "name": "string",
      "confidence": 0.0,
      "reason": "string"
    }
  ],
  "evidence_strength": "strong",
  "open_questions": ["string"]
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for ObservabilityAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "observability_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "confidence" and each subsystem confidence are numbers between 0 and 1.
- Ensure "direction" is one of: "up", "down".
- Ensure metric "severity" is one of: "low", "medium", "high".
- Ensure log "severity" is one of: "info", "warn", "error".
- Ensure "event_type" is one of: "deploy", "config_change", "rollback".
- Ensure "relevance" is one of: "high", "medium", "low".
- Ensure "evidence_strength" is one of: "weak", "moderate", "strong".
- Ensure arrays are arrays of objects with the correct field types.
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


class ObservabilityAgent(BaseAgent):
    name = "observability_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> ObservabilityAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("ObservabilityAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return ObservabilityAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("ObservabilityAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("ObservabilityAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return ObservabilityAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("ObservabilityAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> ObservabilityAgentOutput:
        return ObservabilityAgentOutput(
            agent_name="observability_agent",
            status="failed",
            confidence=0.0,
            summary="Observability agent could not validate the model response and returned a safe fallback result.",
            metric_anomalies=[],
            log_findings=[],
            deployment_findings=[],
            suspected_subsystems=[],
            evidence_strength="weak",
            open_questions=["Review raw observability model output in logs."],
        )
