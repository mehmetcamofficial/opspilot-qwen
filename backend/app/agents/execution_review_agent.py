from typing import Any, Dict

from app.agents.base import BaseAgent
from app.schemas.agents import ExecutionReviewAgentOutput
from app.services.qwen_client import QwenClient


SYSTEM_PROMPT = """
AGENT_ID:execution_review_agent

You are ExecutionReviewAgent in OpsPilot.

Task:
Evaluate observed outcome after remediation.

Rules:
- Use only the supplied evidence.
- Be conservative and operationally safe.
- Return strict JSON matching the required schema.
- Do not include markdown.
- Do not include extra keys.
"""


class ExecutionReviewAgent(BaseAgent):
    name = "execution_review_agent"
    system_prompt = SYSTEM_PROMPT

    def __init__(self, qwen_client: QwenClient) -> None:
        self.qwen_client = qwen_client

    async def run(self, payload: Dict[str, Any]) -> ExecutionReviewAgentOutput:
        raw = await self.qwen_client.generate_json(self.system_prompt, payload)
        return ExecutionReviewAgentOutput.model_validate(raw)
