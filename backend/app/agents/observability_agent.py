from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import ObservabilityAgentOutput
from app.services.qwen_client import QwenClient


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
"""


class ObservabilityAgent(BaseAgent):
    name = "observability_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> ObservabilityAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return ObservabilityAgentOutput.model_validate(raw)
