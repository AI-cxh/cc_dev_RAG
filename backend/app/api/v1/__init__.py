"""API v1 router"""

from fastapi import APIRouter

from app.api.v1 import chat, kbs, config

api_router = APIRouter()

# Include sub-routers
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(kbs.router, prefix="/kbs", tags=["knowledge-base"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
