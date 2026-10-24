# Configuration file for the backend application
from pathlib import Path


from pydantic_settings import SettingsConfigDict , BaseSettings



BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """       Applications settings."""
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str = "My FastAPI Application"
    APP_VERSION: str = "1.0.0"
    OPENAI_API_KEY: str | None = None
    CHECKPOINT_DB: str = str(BASE_DIR / "checkpoints.sqlite")
    MODEL_NAME: str = "qwen3.8-27b"








settings = Settings()
