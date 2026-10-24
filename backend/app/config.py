from pathlib import Path
from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
    )
    APP_NAME: str = "My FastAPI Application"
    APP_VERSION: str = "1.0.0"
    OPENAI_API_KEY: SecretStr | None = None
    GROQ_API_KEY: SecretStr | None = None
    CHECKPOINT_DB: str = str(BASE_DIR / "checkpoints.sqlite")
    GROQ_MODEL_NAME: str = "openai/gpt-oss-120b"
    POSTGRES_HOST: str = "127.0.0.1"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "harvey"
    POSTGRES_PASSWORD: SecretStr | None = None
    POSTGRES_DB: str = "harvey_db"
    REDIS_URL: str = "redis://127.0.0.1:6379/0"

settings = Settings()
