"""
Application launcher.

Creates the FastAPI app, registers routers, and manages the database lifespan.
"""

# TODO: lifespan
# Standard Library Imports
import logging

# Third-Party Imports
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

# Local/First-Party Imports
from app.config import config
from app.middleware import (
    app_exception_handler,
    generic_exception_handler,
    setup_logging,  # noqa: F401,
    validation_exception_handler,
)
from app.utils.errors import AppException

logger = logging.getLogger(__name__)

app = FastAPI(
    title=config.app_name,
    description="A conversational AI service powered by OpenAI.",
    version=config.version,
)  # TODO:  lifespan, swagger_ui_parameters, etc.

# TODO: app include routers here

app.add_exception_handler(AppException, app_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
