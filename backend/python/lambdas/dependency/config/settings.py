from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # search
    OPENSEARCH_ENDPOINT: Optional[str] = None
    # ai
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_EMBED_MODEL: Optional[str] = None
    # storage
    RAW_VENUES_BUCKET: Optional[str] = None
    PROCESSED_VENUES_BUCKET: Optional[str] = None
    # wolt
    WOLT_API_BASE: Optional[str] = None
    VENUE_CATEGORIES_URI: Optional[str] = None
    VENUE_MENU_URI: Optional[str] = None
    # misc
    REGION: str = "eu-west-1"

    def __getattr__(self, name):
        value = super().__getattr__(name)
        if value is None:
            raise AttributeError(f"Setting '{name}' is not set")
        return value


settings = Settings()