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
    GROQ_MODEL_NAME: str = "openai/gpt-oss-120b"
    CHECKPOINT_DB: str = str(BASE_DIR / "checkpoints.sqlite")
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str | None = None
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    # Optional cloud URLs; LANGGRAPH_DATABASE_URL takes priority.
    DATABASE_URL: SecretStr | None = None
    LANGGRAPH_DATABASE_URL: SecretStr | None = None
    POSTGRES_SSLMODE: str = "require"
    LANGGRAPH_POOL_MIN_SIZE: int = 1
    LANGGRAPH_POOL_MAX_SIZE: int = 5

settings = Settings()
