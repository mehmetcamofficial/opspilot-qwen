from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import RemediationPlannerAgentOutput
from app.services.qwen_client import QwenClient


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
"""


class RemediationPlannerAgent(BaseAgent):
    name = "remediation_planner_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> RemediationPlannerAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return RemediationPlannerAgentOutput.model_validate(raw)
