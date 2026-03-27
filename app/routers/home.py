"""
This module defines the API route for the root endpoint,
which provides basic information about the service.

"""

from fastapi import APIRouter

from ..core.config import config

router = APIRouter(tags=["System"])


@router.get("/")
def read_root():
    return {
        "message": config.app_name,
        "version": config.version,
        "docs": "/docs",
        "endpoints": {
            "health": "/health",
            "chat": "/chat",
        },
    }
