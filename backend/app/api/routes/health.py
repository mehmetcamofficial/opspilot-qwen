from fastapi import APIRouter
from app.core.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def healthcheck():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "mock_llm": settings.USE_MOCK_LLM
    }
