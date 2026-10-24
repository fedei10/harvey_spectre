# Configuration file for the backend application
from pathlib import Path


from pydantic_settings import SettingsConfigDict , BaseSettings



BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    """       Applications settings."""
    APP_NAME: str = "My FastAPI Application"
    APP_VERSION: str = "1.0.0"
    CODE_CRAFT_API_KEY: str | None = None





model_config = SettingsConfigDict(env_file=BASE_DIR / ".env", env_file_encoding="utf-8",extra="ignore")



settings = Settings()