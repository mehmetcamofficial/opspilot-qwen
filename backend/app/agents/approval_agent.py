import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import ApprovalAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
AGENT_ID:approval_agent

You are ApprovalAgent in OpsPilot.

Task:
Prepare a concise approval brief for a human operator.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "approval_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "confidence" must be a number between 0 and 1.
- "approval_required" must be a boolean.
- "approval_title" must be a string.
- "incident_summary" must be a string.
- "leading_hypothesis" must be a string.
- "proposed_action" must be a string.
- "expected_impact" must be a string.
- "risk_statement" must be a string.
- "post_action_checks" must be an array of strings.
- "operator_choices" must be an array where each item is exactly one of:
  "approve", "reject", "request_more_data".
- If approval cannot be determined, use:
  approval_required=True,
  status="insufficient_evidence",
  and explain which evidence is missing.

Return JSON with exactly these keys:
{
  "agent_name": "approval_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "approval_required": true,
  "approval_title": "string",
  "incident_summary": "string",
  "leading_hypothesis": "string",
  "proposed_action": "string",
  "expected_impact": "string",
  "risk_statement": "string",
  "post_action_checks": ["string"],
  "operator_choices": ["approve", "reject", "request_more_data"]
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for ApprovalAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "approval_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "confidence" is a number between 0 and 1.
- Ensure "approval_required" is a boolean.
- Ensure "operator_choices" is an array where each item is one of: "approve", "reject", "request_more_data".
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


class ApprovalAgent(BaseAgent):
    name = "approval_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> ApprovalAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("ApprovalAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return ApprovalAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("ApprovalAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("ApprovalAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return ApprovalAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("ApprovalAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> ApprovalAgentOutput:
        return ApprovalAgentOutput(
            agent_name="approval_agent",
            status="failed",
            confidence=0.0,
            summary="Approval agent could not validate the model response and returned a safe fallback result.",
            approval_required=True,
            approval_title="Manual review required",
            incident_summary="Approval brief could not be generated automatically.",
            leading_hypothesis="Unknown — model output could not be validated.",
            proposed_action="Escalate to human operator for manual review.",
            expected_impact="Human operator reviews incident context manually.",
            risk_statement="Model output could not be validated; all actions should require human approval.",
            post_action_checks=["Review raw approval model output in logs."],
            operator_choices=["approve", "reject", "request_more_data"],
        )
