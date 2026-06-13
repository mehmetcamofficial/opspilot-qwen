from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import ApprovalAgentOutput
from app.services.qwen_client import QwenClient


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
"""


class ApprovalAgent(BaseAgent):
    name = "approval_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> ApprovalAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return ApprovalAgentOutput.model_validate(raw)
