import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    postgres_user: str
    postgres_password: str
    postgres_db: str
    postgres_port: int

    jwt_secret_key: str
    jwt_access_token_expire_minutes: int = 120

    model_config = SettingsConfigDict(
        env_file="../.env.local",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        # Trik: Cek apakah ada file atau environment variable yang menandakan kita di Docker
        # Biasanya Docker memberikan env var khusus, atau kita bisa cek file /proc/1/cgroup
        is_docker = os.path.exists('/.dockerenv')
        
        # Kalau di Docker pakai host.docker.internal, kalau di Mac pakai localhost
        host = "host.docker.internal" if is_docker else "localhost"
        
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()
