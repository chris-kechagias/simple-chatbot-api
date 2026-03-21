# Third-Party Imports
from sqlmodel import Field, SQLModel

# Local/First-Party Imports
from ..core.config import config


class HealthResponse(SQLModel):
    """
    Schema for the health check endpoint response.

    This simple model ensures that the API returns a consistent structure
    for health checks, which can be easily extended in the future if needed.
    """

    status: str = Field(
        default="ok",
        description="Indicates the health status of the API. Expected to be 'ok' when healthy.",
    )
    uptime: float = Field(
        default=0.0,
        description="The uptime of the API in seconds. Useful for monitoring and diagnostics.",
    )
    version: str = Field(
        default=config.version, description="The current version of the API."
    )
