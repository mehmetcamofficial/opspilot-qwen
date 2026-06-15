import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.incidents import router as incidents_router

logger = logging.getLogger(__name__)

app = FastAPI(title=settings.APP_NAME)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(incidents_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler for all unhandled exceptions."""
    error_id = f"err-{uuid.uuid4().hex[:12]}"

    logger.error(
        f"Unhandled exception [{error_id}]: {type(exc).__name__}: {str(exc)}",
        exc_info=exc
    )

    # Return structured error response
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "id": error_id,
                "type": type(exc).__name__,
                "message": "An error occurred while processing your request. Please try again.",
                "details": str(exc) if settings.APP_ENV == "dev" else None
            }
        }
    )


@app.get("/")
async def root():
    return {
        "message": "OpsPilot Backend is running",
        "docs": "/docs",
        "health": "/health",
        "incidents": "/incidents"
    }
