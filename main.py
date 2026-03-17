"""
Application launcher.

Creates the FastAPI app, registers routers, and manages the database lifespan.
"""

# TODO: logger = logging.getLogger(__name__)
# TODO: lifespan
# Third-Party Imports
from fastapi import FastAPI

# Local/First-Party Imports
from app.config import config

app = FastAPI(
    title=config.app_name,
    description="A conversational AI service powered by OpenAI.",
    version=config.version,
)  # TODO:  lifespan, swagger_ui_parameters, etc.

# TODO: app include routers here

# TODO: error handlers here
