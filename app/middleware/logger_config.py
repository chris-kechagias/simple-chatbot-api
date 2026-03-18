# Standard Library Imports
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

from pythonjsonlogger import jsonlogger


def setup_logging():
    """
    Configures the root logger with console output.

    Sets up INFO-level logging with timestamps and module names.
    Prevents duplicate handler registration.
    """

    # 1. Get the root logger
    root_logger = logging.getLogger()

    # Prevent duplicate handlers
    if not root_logger.handlers:
        root_logger.setLevel(logging.INFO)

        # Create JSON formatter (structured logging)
        json_formatter = jsonlogger.JsonFormatter(
            fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
            rename_fields={"levelname": "level", "asctime": "timestamp"},
        )

        # 1. Console Handler (for Render/Docker)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(json_formatter)
        root_logger.addHandler(console_handler)

        # 2. File Handler (for local debugging)
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        file_handler = RotatingFileHandler(
            "logs/app.log",
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=3,
        )
        file_handler.setFormatter(json_formatter)
        root_logger.addHandler(file_handler)


# Initialize logging at module import
setup_logging()
