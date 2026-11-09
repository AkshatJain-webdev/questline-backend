from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Real environment variables win over .env; .env is for local overrides only.
    model_config = SettingsConfigDict(env_file=".env")

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db_name: str = "questline"
    # Set as a JSON list in the environment, e.g. ["https://app.example.com"].
    cors_allowed_origins: list[str] = ["http://localhost:3000"]


settings = Settings()
