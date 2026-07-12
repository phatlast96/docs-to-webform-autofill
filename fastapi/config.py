from pydantic_settings import BaseSettings, SettingsConfigDict

FORM_URL = "https://mendrika-alma.github.io/form-submission/"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    form_url: str = FORM_URL
    playwright_headful: bool = False
    debug: bool = False


settings = Settings()
