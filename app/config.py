"""Configuration — loaded from environment variables via pydantic-settings"""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Bolna
    bolna_api_key: str = Field(..., description="Bolna API key (Bearer token)")
    bolna_api_base_url: str = Field(
        default="https://api.bolna.ai",
        description="Bolna API base URL",
    )

    # Slack
    slack_webhook_url: str = Field(..., description="Slack Incoming Webhook URL")

    # Server
    port: int = Field(default=8000, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment name")

    # Tuning
    max_retries: int = Field(default=3, description="Max API retry attempts")
    retry_delay: int = Field(default=1, description="Initial retry delay (seconds)")
    request_timeout: int = Field(default=30, description="HTTP request timeout (seconds)")
    max_transcript_length: int = Field(
        default=3000, description="Max transcript chars in Slack message"
    )

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


settings = Settings()
