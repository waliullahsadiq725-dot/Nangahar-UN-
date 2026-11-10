from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    app_name: str = "Nangarhar University Digital Library API"
    secret_key: str
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./nudl.db"
    upload_dir: str = "./uploads"
    max_upload_mb: int = 25
    cors_origins: str = "http://127.0.0.1:5500,http://localhost:5500"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
