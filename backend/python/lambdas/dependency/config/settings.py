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
    USER_SETTINGS_BUCKET: Optional[str] = None
    SEARCH_RESULTS_BUCKET: Optional[str] = None
    # wolt
    VENUES_ENDPOINT: Optional[str] = None
    WOLT_API_BASE: Optional[str] = None
    VENUE_CATEGORIES_URI: Optional[str] = None
    VENUE_MENU_URI: Optional[str] = None
    VENUE_DETAILS_URI: Optional[str] = None
    LATITUDE: Optional[float] = None
    LONGITUDE: Optional[float] = None
    # telegram
    TELEGRAM_API_URL: str = "https://api.telegram.org/bot{key}"
    TELEGRAM_TOKEN: Optional[str] = None
    TELEGRAM_REQUEST_HEADER: Optional[str] = None
    # misc
    SEARCH_MACHINE_ARN: Optional[str] = None
    REGION: str = "eu-west-1"

    def __getattr__(self, name):
        value = super().__getattr__(name)
        if value is None:
            raise AttributeError(f"Setting '{name}' is not set")
        return value

    class Config:
        env_file = ".env"


settings = Settings()