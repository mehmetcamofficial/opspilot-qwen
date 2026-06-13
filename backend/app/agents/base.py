from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    name: str = "base_agent"
    system_prompt: str = ""

    @abstractmethod
    async def run(self, payload: Dict[str, Any]) -> Any:
        raise NotImplementedError
