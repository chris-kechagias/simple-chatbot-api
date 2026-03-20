# Standard Library Imports
import time

# Third-Party Imports
from fastapi import APIRouter

# Local/First-Party Imports
from ..config import config
from ..models import HealthResponse

router = APIRouter(tags=["System"])


@router.head("/health")
@router.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok", version=config.version, uptime=time.time() - config.start_time
    )
