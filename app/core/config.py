# Standard Library Imports
import time

# Third-Party Imports
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
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
    openai_model: str = "gpt-5-mini"
    openai_system_prompt: str = ""
    openai_max_completion_tokens: int = 1000
    context_window_size: int = 15

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


config = Settings()
