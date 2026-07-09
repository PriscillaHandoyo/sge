import os
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_user: str = "sge"
    postgres_password: str = "sge"
    postgres_db: str = "sge"
    postgres_port: str = "5432"
    postgres_host: Optional[str] = None  # kalau diisi eksplisit (lewat env var), ini yang menang
    jwt_secret_key: str = "sgesecretkey18"
    jwt_access_token_expire_minutes: int = 120

    model_config = SettingsConfigDict(
        env_file="../.env.local",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        if self.postgres_host:
            # Production/server: host di-set eksplisit lewat env var
            # (misal "sge-db" — nama service Postgres di docker-compose)
            host = self.postgres_host
        else:
            # Fallback buat dev lokal Mac: di dalam Docker -> host.docker.internal
            # (Postgres jalan native di Mac host), kalau bukan Docker -> localhost
            is_docker = os.path.exists('/.dockerenv')
            host = "host.docker.internal" if is_docker else "localhost"
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{host}:{self.postgres_port}/{self.postgres_db}"


settings = Settings()
