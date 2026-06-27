import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import ExecutionReviewAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
AGENT_ID:execution_review_agent

You are ExecutionReviewAgent in OpsPilot.

Task:
Evaluate observed outcome after remediation.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "execution_review_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "confidence" must be a number between 0 and 1.
- "outcome" must be exactly one of: "resolved", "improved", "unchanged", "worsened", "inconclusive".
- "metric_changes" must be an array of objects with:
  "metric_name" (string), "before" (number), "after" (number),
  "interpretation" (string).
- "resolution_confidence" must be a number between 0 and 1.
- "recommended_next_step" must be a string.
- If outcome cannot be determined, use:
  outcome="inconclusive",
  resolution_confidence=0.0,
  and explain which evidence is missing.

Return JSON with exactly these keys:
{
  "agent_name": "execution_review_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "outcome": "improved",
  "metric_changes": [
    {
      "metric_name": "string",
      "before": 0.0,
      "after": 0.0,
      "interpretation": "string"
    }
  ],
  "resolution_confidence": 0.0,
  "recommended_next_step": "string"
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for ExecutionReviewAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "execution_review_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "confidence" is a number between 0 and 1.
- Ensure "outcome" is one of: "resolved", "improved", "unchanged", "worsened", "inconclusive".
- Ensure "resolution_confidence" is a number between 0 and 1.
- Ensure "metric_changes" is an array of objects with the correct field types.
- Ensure "recommended_next_step" is a string.
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


class ExecutionReviewAgent(BaseAgent):
    name = "execution_review_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> ExecutionReviewAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("ExecutionReviewAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return ExecutionReviewAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("ExecutionReviewAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("ExecutionReviewAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return ExecutionReviewAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("ExecutionReviewAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> ExecutionReviewAgentOutput:
        return ExecutionReviewAgentOutput(
            agent_name="execution_review_agent",
            status="failed",
            confidence=0.0,
            summary="Execution review agent could not validate the model response and returned a safe fallback result.",
            outcome="inconclusive",
            metric_changes=[],
            resolution_confidence=0.0,
            recommended_next_step="Review raw execution review model output in logs.",
        )
