from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import HypothesisAgentOutput
from app.services.qwen_client import QwenClient


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
"""


class HypothesisAgent(BaseAgent):
    name = "hypothesis_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> HypothesisAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return HypothesisAgentOutput.model_validate(raw)
