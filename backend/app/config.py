# Configuration file for the backend application
from pathlib import Path


from pydantic_settings import SettingsConfigDict , BaseSettings
from pydantic import SecretStr


BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """       Applications settings."""
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str = "My FastAPI Application"
    APP_VERSION: str = "1.0.0"
    OPENAI_API_KEY: SecretStr | None = None
    GROQ_API_KEY: SecretStr | None = None
    CHECKPOINT_DB: str = str(BASE_DIR / "checkpoints.sqlite")
    GROQ_MODEL_NAME: str = "openai/gpt-oss-120b"








settings = Settings()
