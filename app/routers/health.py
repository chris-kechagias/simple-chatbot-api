"""
This module defines the API route for the health check endpoint,
which allows clients to verify that the service is running and healthy.

"""

import time

from fastapi import APIRouter

from ..core.config import config
from ..models import HealthResponse

router = APIRouter(tags=["System"])


@router.head("/health")
@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok", version=config.version, uptime=time.time() - config.start_time
    )
