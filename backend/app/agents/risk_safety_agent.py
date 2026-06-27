import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import RiskSafetyAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
AGENT_ID:risk_safety_agent

You are RiskSafetyAgent in OpsPilot.

Task:
Assess remediation actions for operational safety and policy compliance.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "risk_safety_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "confidence" must be a number between 0 and 1.
- "action_reviews" must be an array of objects with:
  "action_id" (string),
  "risk_score" (number between 0 and 1),
  "risk_level" (one of: "low", "medium", "high"),
  "policy_decision" (one of: "allow_auto", "require_approval", "block"),
  "key_risk_factors" (array of strings),
  "recommended_guardrails" (array of strings),
  "reason" (string).
- "recommended_action_id" must be a string matching one of the reviewed action_ids.
- If evidence is limited, use:
  status="insufficient_evidence",
  policy_decision="require_approval",
  and explain which evidence is missing.

Return JSON with exactly these keys:
{
  "agent_name": "risk_safety_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "action_reviews": [
    {
      "action_id": "string",
      "risk_score": 0.0,
      "risk_level": "medium",
      "policy_decision": "require_approval",
      "key_risk_factors": ["string"],
      "recommended_guardrails": ["string"],
      "reason": "string"
    }
  ],
  "recommended_action_id": "string"
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for RiskSafetyAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "risk_safety_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "confidence" is a number between 0 and 1.
- Ensure "risk_score" is a number between 0 and 1.
- Ensure "risk_level" is one of: "low", "medium", "high".
- Ensure "policy_decision" is one of: "allow_auto", "require_approval", "block".
- Ensure "recommended_action_id" matches one of the reviewed action_ids.
- Ensure arrays are arrays of strings as required.
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


class RiskSafetyAgent(BaseAgent):
    name = "risk_safety_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> RiskSafetyAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("RiskSafetyAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return RiskSafetyAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("RiskSafetyAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("RiskSafetyAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return RiskSafetyAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("RiskSafetyAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> RiskSafetyAgentOutput:
        return RiskSafetyAgentOutput(
            agent_name="risk_safety_agent",
            status="failed",
            confidence=0.0,
            summary="Risk safety agent could not validate the model response and returned a safe fallback result.",
            action_reviews=[
                {
                    "action_id": "act-safe-escalate",
                    "risk_score": 0.0,
                    "risk_level": "low",
                    "policy_decision": "require_approval",
                    "key_risk_factors": ["Model output could not be validated."],
                    "recommended_guardrails": ["Escalate to a human operator before taking automated action."],
                    "reason": "Risk safety agent response could not be validated safely.",
                }
            ],
            recommended_action_id="act-safe-escalate",
        )
