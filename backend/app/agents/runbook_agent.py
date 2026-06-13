from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import RunbookAgentOutput
from app.services.qwen_client import QwenClient


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
"""


class RunbookAgent(BaseAgent):
    name = "runbook_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> RunbookAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return RunbookAgentOutput.model_validate(raw)
