import asyncio
import json
import logging
from typing import Any, Dict

import httpx

from app.core.config import settings
from app.services.mock_qwen_responses import get_mock_response

logger = logging.getLogger(__name__)


class QwenClient:
    def __init__(self) -> None:
        self.api_base = settings.QWEN_API_BASE
        self.api_key = settings.QWEN_API_KEY
        self.model = settings.QWEN_MODEL
        self.use_mock = settings.USE_MOCK_LLM
        self.fallback_to_mock = settings.FALLBACK_TO_MOCK_ON_ERROR
        self.max_retries = 3
        self.timeout = 60.0

    async def generate_json(self, system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        if self.use_mock:
            logger.info("Using mock LLM response")
            return get_mock_response(system_prompt, user_payload)

        try:
            return await self._generate_json_from_qwen_with_retry(system_prompt, user_payload)
        except Exception as exc:
            logger.exception(f"Qwen API call failed after {self.max_retries} retries. Error: {str(exc)}")
            if self.fallback_to_mock:
                logger.info("Falling back to mock LLM response due to API failure")
                return get_mock_response(system_prompt, user_payload)
            raise exc

    async def _generate_json_from_qwen_with_retry(self, system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Call Qwen API with exponential backoff retry logic."""
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                logger.debug(f"Qwen API attempt {attempt + 1}/{self.max_retries}")
                return await self._generate_json_from_qwen(system_prompt, user_payload)
            except (httpx.TimeoutException, httpx.ConnectError, httpx.RemoteProtocolError) as exc:
                last_exception = exc
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                    logger.warning(f"Qwen API attempt {attempt + 1} failed ({type(exc).__name__}). Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"Qwen API attempt {attempt + 1} failed. No more retries.")
            except Exception as exc:
                # Non-retryable errors (malformed response, auth, etc.)
                logger.error(f"Qwen API non-retryable error: {type(exc).__name__}: {str(exc)}")
                raise exc

        if last_exception:
            raise last_exception

    async def _generate_json_from_qwen(self, system_prompt: str, user_payload: Dict[str, Any]) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": json.dumps(user_payload)}
            ],
            "response_format": {"type": "json_object"}
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload
            )
            response.raise_for_status()

        data = response.json()
        content = data.get("choices", [{}])[0].get("message", {}).get("content")

        if content is None:
            raise ValueError("Qwen response did not contain choices[0].message.content")

        if isinstance(content, dict):
            return content

        return json.loads(content)
