import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import TriageAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """
AGENT_ID:triage_agent

You are TriageAgent in OpsPilot.

Task:
Interpret an incoming alert and produce a structured triage decision.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "triage_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "incident_type" must be exactly one of:
  "latency", "error_rate", "availability", "dependency_failure",
  "deployment_regression", "data_integrity", "security_signal", "unknown".
- "severity" must be exactly one of: "low", "medium", "high", "critical".
- "blast_radius" must be exactly one of:
  "single_service", "multi_service", "customer_visible", "unknown".
- "confidence" must be a number between 0 and 1.
- "impacted_services" must be an array of strings.
- "initial_hypotheses" must be an array of objects with:
  "title", "confidence", "reason".
- "recommended_next_steps", "recommended_tools", and "handoff_agents" must be arrays of strings.
- If evidence is limited, use:
  status="insufficient_evidence",
  incident_type="unknown",
  blast_radius="unknown",
  and empty arrays where needed.

Return JSON with exactly these keys:
{
  "agent_name": "triage_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "incident_type": "latency",
  "severity": "medium",
  "business_impact": "string",
  "impacted_services": ["string"],
  "blast_radius": "single_service",
  "initial_hypotheses": [
    {
      "title": "string",
      "confidence": 0.0,
      "reason": "string"
    }
  ],
  "recommended_next_steps": ["string"],
  "recommended_tools": ["string"],
  "handoff_agents": ["string"]
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for TriageAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "triage_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "incident_type" is one of:
  "latency", "error_rate", "availability", "dependency_failure",
  "deployment_regression", "data_integrity", "security_signal", "unknown".
- Ensure "severity" is one of: "low", "medium", "high", "critical".
- Ensure "blast_radius" is one of:
  "single_service", "multi_service", "customer_visible", "unknown".
- Ensure "confidence" and each hypothesis confidence are numbers between 0 and 1.
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


class TriageAgent(BaseAgent):
    name = "triage_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> TriageAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("TriageAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return TriageAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("TriageAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("TriageAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return TriageAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("TriageAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> TriageAgentOutput:
        service = str(payload.get("alert", {}).get("service", "unknown-service"))
        return TriageAgentOutput(
            agent_name="triage_agent",
            status="failed",
            confidence=0.0,
            summary="Triage agent could not validate the model response and returned a safe fallback result.",
            incident_type="unknown",
            severity="medium",
            business_impact=f"Unable to determine business impact for {service} because triage output validation failed.",
            impacted_services=[service],
            blast_radius="unknown",
            initial_hypotheses=[
                {
                    "title": "Model output schema mismatch",
                    "confidence": 0.0,
                    "reason": f"Triage response could not be validated: {error.errors()[0].get('msg', 'unknown validation error')}",
                }
            ],
            recommended_next_steps=[
                "Review the raw triage model output in logs.",
                "Re-run triage with stricter prompt guidance or corrected model settings.",
                "Escalate to an operator if the incident is time-sensitive.",
            ],
            recommended_tools=["logs_tool"],
            handoff_agents=["observability_agent"],
        )
