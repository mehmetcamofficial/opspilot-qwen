import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import RemediationPlannerAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
AGENT_ID:remediation_planner_agent

You are RemediationPlannerAgent in OpsPilot.

Task:
Produce safe remediation options with rollback plans.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "remediation_planner_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "confidence" must be a number between 0 and 1.
- "candidate_actions" must be an array of objects with:
  "action_id" (string), "title" (string),
  "action_type" (one of: "inspect", "rollback_config", "restart_service",
   "scale_worker", "clear_cache", "feature_flag_change",
   "manual_escalation", "other"),
  "priority_rank" (integer >= 1),
  "targets" (array of strings),
  "rationale" (string), "expected_impact" (string),
  "preconditions" (array of strings),
  "rollback_plan" (array of strings),
  "estimated_risk" (one of: "low", "medium", "high"),
  "automation_suitability" (one of: "auto", "approval_required", "manual_only").
- "recommended_primary_action_id" must be a string matching one of the action_ids.
- "mitigation_vs_fix" must be an object with:
  "mitigation_action_ids" (array of strings),
  "root_cause_fix_action_ids" (array of strings).
- If remediation options are unclear, use:
  status="insufficient_evidence",
  a single safe escalate action,
  and explain which evidence is missing.

Return JSON with exactly these keys:
{
  "agent_name": "remediation_planner_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "candidate_actions": [
    {
      "action_id": "string",
      "title": "string",
      "action_type": "manual_escalation",
      "priority_rank": 1,
      "targets": ["string"],
      "rationale": "string",
      "expected_impact": "string",
      "preconditions": ["string"],
      "rollback_plan": ["string"],
      "estimated_risk": "low",
      "automation_suitability": "manual_only"
    }
  ],
  "recommended_primary_action_id": "string",
  "mitigation_vs_fix": {
    "mitigation_action_ids": ["string"],
    "root_cause_fix_action_ids": ["string"]
  }
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for RemediationPlannerAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "remediation_planner_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "confidence" is a number between 0 and 1.
- Ensure "action_type" is one of: "inspect", "rollback_config", "restart_service",
  "scale_worker", "clear_cache", "feature_flag_change",
  "manual_escalation", "other".
- Ensure "estimated_risk" is one of: "low", "medium", "high".
- Ensure "automation_suitability" is one of: "auto", "approval_required", "manual_only".
- Ensure "priority_rank" is an integer >= 1.
- Ensure "recommended_primary_action_id" matches one of the candidate action_ids.
- Ensure "mitigation_vs_fix" contains both "mitigation_action_ids" and "root_cause_fix_action_ids" arrays.
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


class RemediationPlannerAgent(BaseAgent):
    name = "remediation_planner_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> RemediationPlannerAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("RemediationPlannerAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return RemediationPlannerAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("RemediationPlannerAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("RemediationPlannerAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return RemediationPlannerAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("RemediationPlannerAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> RemediationPlannerAgentOutput:
        return RemediationPlannerAgentOutput(
            agent_name="remediation_planner_agent",
            status="failed",
            confidence=0.0,
            summary="Remediation planner agent could not validate the model response and returned a safe fallback result.",
            candidate_actions=[
                {
                    "action_id": "act-safe-escalate",
                    "title": "Escalate to human operator",
                    "action_type": "manual_escalation",
                    "priority_rank": 1,
                    "targets": ["incident_commander"],
                    "rationale": "Model output could not be validated safely.",
                    "expected_impact": "Human operator reviews remediation manually.",
                    "preconditions": ["Incident context is available."],
                    "rollback_plan": ["No automated action was executed."],
                    "estimated_risk": "low",
                    "automation_suitability": "manual_only",
                }
            ],
            recommended_primary_action_id="act-safe-escalate",
            mitigation_vs_fix={
                "mitigation_action_ids": ["act-safe-escalate"],
                "root_cause_fix_action_ids": [],
            },
        )
