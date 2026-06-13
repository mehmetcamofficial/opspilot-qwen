from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.incidents import router as incidents_router

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


@app.get("/")
async def root():
    return {
        "message": "OpsPilot Backend is running",
        "docs": "/docs",
        "health": "/health",
        "incidents": "/incidents"
    }
