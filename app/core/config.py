"""
This module defines the application settings using Pydantic's BaseSettings.
It loads configuration from environment variables and .env files,
providing a single source of truth for all configurable parameters in the app.

"""

import time

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""
    app_name: str = "Simple Chatbot API"
    version: str = "0.0.0"
    debug: bool = False
    db_username: str = ""
    db_password: str = ""
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "chatbot_db"
    start_time: float = time.time()
    openai_api_key: str = ""
    openai_model: str = "gpt-5.4-mini"
    openai_utility_model: str = "gpt-5.4-nano"
    openai_max_completion_tokens: int = 8000
    openai_max_input_tokens: int = 4000
    context_window_size: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


config = Settings()
