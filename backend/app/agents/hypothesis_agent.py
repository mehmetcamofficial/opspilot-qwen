import json
import logging
from typing import Any, Dict

from pydantic import ValidationError

from app.agents.base import BaseAgent
from app.schemas.agents import HypothesisAgentOutput
from app.services.qwen_client import QwenClient

logger = logging.getLogger(__name__)


SYSTEM_PROMPT = """
AGENT_ID:hypothesis_agent

You are HypothesisAgent in OpsPilot.

Task:
Generate ranked root-cause hypotheses based on evidence.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
- Return exactly one JSON object.
- Every required field must be present, even when evidence is weak.
- "agent_name" must always be "hypothesis_agent".
- "status" must be exactly one of: "success", "insufficient_evidence", "failed".
- "confidence" must be a number between 0 and 1.
- "hypotheses" must be an array of objects with:
  "title" (string), "confidence" (number between 0 and 1),
  "likelihood_rank" (integer >= 1, 1 is most likely),
  "supporting_evidence" (array of strings),
  "contradicting_evidence" (array of strings),
  "blast_radius_if_true" (string),
  "next_validation_step" (string).
- "leading_hypothesis" must be an object with:
  "title" (string), "confidence" (number between 0 and 1), "reason" (string).
- "unknowns" must be an array of strings.
- If evidence is limited, use:
  status="insufficient_evidence",
  a single low-confidence hypothesis,
  and meaningful unknowns.

Return JSON with exactly these keys:
{
  "agent_name": "hypothesis_agent",
  "status": "success",
  "confidence": 0.0,
  "summary": "string",
  "hypotheses": [
    {
      "title": "string",
      "confidence": 0.0,
      "likelihood_rank": 1,
      "supporting_evidence": ["string"],
      "contradicting_evidence": ["string"],
      "blast_radius_if_true": "string",
      "next_validation_step": "string"
    }
  ],
  "leading_hypothesis": {
    "title": "string",
    "confidence": 0.0,
    "reason": "string"
  },
  "unknowns": ["string"]
}
"""

REPAIR_PROMPT = """
You previously returned JSON that failed schema validation for HypothesisAgentOutput.

Repair the response so it matches the schema exactly.

Requirements:
- Return exactly one JSON object.
- Do not include markdown.
- Do not include explanations.
- Do not include extra keys.
- Preserve the original meaning where possible.
- Fix invalid enum values.
- Add every missing required field.
- Ensure "agent_name" is exactly "hypothesis_agent".
- Ensure "status" is one of: "success", "insufficient_evidence", "failed".
- Ensure "confidence" and each hypothesis and leading_hypothesis confidence are numbers between 0 and 1.
- Ensure "likelihood_rank" is an integer >= 1.
- Ensure "hypotheses" is an array of objects with all required fields.
- Ensure "leading_hypothesis" is an object with "title", "confidence", and "reason".
- Ensure "unknowns" is an array of strings.
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


class HypothesisAgent(BaseAgent):
    name = "hypothesis_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> HypothesisAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        logger.info("HypothesisAgent raw Qwen response: %s", json.dumps(_mask_secrets(raw), ensure_ascii=True))

        try:
            return HypothesisAgentOutput.model_validate(raw)
        except ValidationError as error:
            logger.warning("HypothesisAgent validation failed on initial response: %s", error)
            repair_payload = {
                "original_payload": payload,
                "invalid_response": raw,
                "validation_errors": _validation_error_details(error),
            }
            repaired_raw = await self.qwen_client.generate_json(REPAIR_PROMPT, repair_payload)
            logger.info("HypothesisAgent repaired Qwen response: %s", json.dumps(_mask_secrets(repaired_raw), ensure_ascii=True))

            try:
                return HypothesisAgentOutput.model_validate(repaired_raw)
            except ValidationError as repair_error:
                logger.error("HypothesisAgent validation failed after repair: %s", repair_error)
                return self._graceful_failure_output(payload, repair_error)

    def _graceful_failure_output(self, payload: Dict[str, Any], error: ValidationError) -> HypothesisAgentOutput:
        return HypothesisAgentOutput(
            agent_name="hypothesis_agent",
            status="failed",
            confidence=0.0,
            summary="Hypothesis agent could not validate the model response and returned a safe fallback result.",
            hypotheses=[
                {
                    "title": "Model output schema mismatch",
                    "confidence": 0.0,
                    "likelihood_rank": 1,
                    "supporting_evidence": [],
                    "contradicting_evidence": [],
                    "blast_radius_if_true": "unknown",
                    "next_validation_step": "Review raw hypothesis model output in logs.",
                }
            ],
            leading_hypothesis={
                "title": "Model output schema mismatch",
                "confidence": 0.0,
                "reason": "Hypothesis agent response could not be validated.",
            },
            unknowns=["Review raw hypothesis model output in logs."],
        )
