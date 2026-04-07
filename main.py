"""
Application launcher.

Creates the FastAPI app, registers routers, and manages the database lifespan.
"""

# Standard Library Imports
import logging
from contextlib import asynccontextmanager

# Third-Party Imports
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

# Local/First-Party Imports
from app.core import config, create_db_and_tables, setup_logging  # noqa: F401
from app.core.errors import (
    AppException,
    DatabaseException,
    app_exception_handler,
    generic_exception_handler,
    validation_exception_handler,
)
from app.middleware import security_headers_middleware  # noqa: F401
from app.routers import chat_router, health_router, home_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles the application startup and shutdown events.

    Ensures the database engine is ready and tables are created before
    the API starts accepting traffic.
    """
    logger.info(
        "Lifespan Startup: Verifying database connectivity and creating tables."
    )
    # This ensures the database is ready before the first request arrives.
    try:
        create_db_and_tables()
    except Exception as e:
        raise DatabaseException(details={"error": str(e)})
    yield
    logger.info("Lifespan Shutdown: Cleaning up resources.")


app = FastAPI(
    title=config.app_name,
    description="A conversational AI service powered by OpenAI.",
    version=config.version,
    lifespan=lifespan,
    swagger_ui_parameters={"docExpansion": "none"},
)

app.middleware("http")(security_headers_middleware)

app.include_router(health_router)
app.include_router(home_router)
app.include_router(chat_router)

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
