from pydantic_settings import BaseSettings, SettingsConfigDict

from app.version import VERSION as APP_VERSION


class Settings(BaseSettings):
    PROJECT_NAME: str = "Velide by Baloide"
    VERSION: str = APP_VERSION
    API_PREFIX: str = "/api"
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")


settings = Settings()
