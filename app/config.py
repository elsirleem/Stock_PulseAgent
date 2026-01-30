"""
Configuration management for StockPulse Agent.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    
    # Twilio Configuration
    twilio_account_sid: str = ""
    twilio_auth_token: str = ""
    twilio_whatsapp_number: str = "whatsapp:+14155238886"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Daily Update Schedule
    daily_update_hour: int = 8
    daily_update_minute: int = 30
    
    # Database
    database_url: str = "sqlite:///./stockpulse.db"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
