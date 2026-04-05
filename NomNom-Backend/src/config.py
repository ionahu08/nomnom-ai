from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nomnom"

    # Auth
    jwt_secret_key: str = "change-me-to-a-random-secret-at-least-32b"
    jwt_algorithm: str = "HS256"
    jwt_expiry_minutes: int = 1440

    # Anthropic
    anthropic_api_key: str = ""

    # Photo uploads
    upload_dir: str = "uploads"

    model_config = {"env_file": ".env", "extra": "ignore"}


settings = Settings()
