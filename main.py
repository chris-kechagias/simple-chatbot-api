"""
Application launcher.

Creates the FastAPI app, registers routers, and manages the database lifespan.
"""

# TODO: logger = logging.getLogger(__name__)
# TODO: lifespan

from fastapi import FastAPI

app = (
    FastAPI()
)  # TODO: title, description, version, lifespan, swagger_ui_parameters, etc.

# TODO: app include routers here

# TODO: error handlers here
