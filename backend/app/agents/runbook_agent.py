import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import RunbookAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
AGENT_ID:runbook_agent

You are RunbookAgent in OpsPilot.

Task:
Retrieve and summarize relevant runbooks and prior incidents.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "runbook_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "confidence" must be a number between 0 and 1.
- "top_matches" must be an array of objects with:
  "doc_id" (string), "doc_type" (one of: "runbook", "sop", "prior_incident"),
  "title" (string), "relevance" (one of: "high", "medium", "low"),
  "reason" (string).
- "recommended_diagnostic_steps" must be an array of objects with:
  "step" (string), "source_doc_id" (string),
  "source_type" (one of: "runbook", "sop", "prior_incident").
- "recommended_remediation_steps" must be an array of objects with:
  "step" (string), "source_doc_id" (string),
  "source_type" (one of: "runbook", "sop", "prior_incident"),
  "risk_level" (one of: "low", "medium", "high").
- "rollback_notes", "operational_risks", "gaps_or_missing_guidance" must be arrays of strings.
- If no relevant runbooks are found, use:
  status="insufficient_evidence",
  and empty arrays where needed.

Return JSON with exactly these keys:
{
  "agent_name": "runbook_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "top_matches": [
    {
      "doc_id": "string",
      "doc_type": "runbook",
      "title": "string",
      "relevance": "high",
      "reason": "string"
    }
  ],
  "recommended_diagnostic_steps": [
    {
      "step": "string",
      "source_doc_id": "string",
      "source_type": "runbook"
    }
  ],
  "recommended_remediation_steps": [
    {
      "step": "string",
      "source_doc_id": "string",
      "source_type": "runbook",
      "risk_level": "low"
    }
  ],
  "rollback_notes": ["string"],
  "operational_risks": ["string"],
  "gaps_or_missing_guidance": ["string"]
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for RunbookAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "runbook_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "confidence" is a number between 0 and 1.
- Ensure "doc_type" is one of: "runbook", "sop", "prior_incident".
- Ensure "relevance" is one of: "high", "medium", "low".
- Ensure "source_type" is one of: "runbook", "sop", "prior_incident".
- Ensure "risk_level" is one of: "low", "medium", "high".
- Ensure arrays are arrays of objects or strings as required.
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


class RunbookAgent(BaseAgent):
    name = "runbook_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> RunbookAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("RunbookAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return RunbookAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("RunbookAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("RunbookAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return RunbookAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("RunbookAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> RunbookAgentOutput:
        return RunbookAgentOutput(
            agent_name="runbook_agent",
            status="failed",
            confidence=0.0,
            summary="Runbook agent could not validate the model response and returned a safe fallback result.",
            top_matches=[],
            recommended_diagnostic_steps=[],
            recommended_remediation_steps=[],
            rollback_notes=[],
            operational_risks=[],
            gaps_or_missing_guidance=["Review raw runbook model output in logs."],
        )
