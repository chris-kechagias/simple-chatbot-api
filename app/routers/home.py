# Third-Party Imports
from fastapi import APIRouter

# Local/First-Party Imports
from ..config import config

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
