"""Configuration management using Pydantic Settings"""

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Bolna Configuration
    bolna_api_key: str = Field(..., description="Bolna API authentication key")
    bolna_api_base_url: str = Field(
        default="https://api.bolna.dev",
        description="Bolna API base URL"
    )
    bolna_webhook_secret: str | None = Field(
        default=None,
        description="Optional webhook verification secret"
    )
    
    # Slack Configuration
    slack_webhook_url: str = Field(..., description="Slack incoming webhook URL")
    
    # Server Configuration
    port: int = Field(default=8000, description="Server port")
    host: str = Field(default="0.0.0.0", description="Server host")
    log_level: str = Field(default="INFO", description="Logging level")
    environment: str = Field(default="development", description="Environment name")
    
    # Optional Configuration
    max_retries: int = Field(default=3, description="Maximum API retry attempts")
    retry_delay: int = Field(default=1, description="Initial retry delay in seconds")
    request_timeout: int = Field(default=30, description="HTTP request timeout")
    max_transcript_length: int = Field(
        default=3000,
        description="Maximum transcript length in Slack message"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()

# Made with Bob
