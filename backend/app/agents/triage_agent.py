from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import TriageAgentOutput
from app.services.qwen_client import QwenClient


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
"""


class TriageAgent(BaseAgent):
    name = "triage_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> TriageAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return TriageAgentOutput.model_validate(raw)
