from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import PostmortemAgentOutput
from app.services.qwen_client import QwenClient


SYSTEM_PROMPT = """
AGENT_ID:postmortem_agent

You are PostmortemAgent in OpsPilot.

Task:
Create a concise incident postmortem report.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
"""


class PostmortemAgent(BaseAgent):
    name = "postmortem_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> PostmortemAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return PostmortemAgentOutput.model_validate(raw)
