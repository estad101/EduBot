"""
Application settings and configuration management.
Supports WhatsApp Cloud API directly (no n8n needed)."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application configuration."""

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"  # Allow extra fields from .env that aren't defined
    )

    # Database
    database_url: str = "mysql+pymysql://chatbot_user:ChatbotSecure123!@localhost:3306/chatbot"
    
    # FastAPI
    debug: bool = False
    api_title: str = "WhatsApp Chatbot API"
    api_version: str = "1.0.0"
    api_port: int = 8000

    # Paystack (optional for now)
    paystack_public_key: Optional[str] = None
    paystack_secret_key: Optional[str] = None
    paystack_webhook_secret: Optional[str] = None
    paystack_webhook_url: Optional[str] = "http://localhost:8000/api/payments/webhook/paystack"
    
    # WhatsApp
    whatsapp_api_key: str
    phone_number_id: Optional[str] = None
    business_account_id: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None
    whatsapp_webhook_token: Optional[str] = None

    # File Upload
    max_file_size_mb: int = 5
    allowed_image_types: str = "image/jpeg,image/png,image/webp"
    uploads_dir: str = "uploads"

    # Security
    secret_key: Optional[str] = "your-secret-key"
    algorithm: str = "HS256"
    admin_origin: str = "http://localhost:3000"
    allow_origins: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000"
    https_only: bool = False
    session_timeout_minutes: int = 60
    rate_limit_per_minute: int = 60

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/chatbot.log"

    # Monitoring & Error Tracking
    sentry_dsn: Optional[str] = None
    environment: str = "production"

    @property
    def allowed_mime_types(self) -> list[str]:
        """Get allowed MIME types as list."""
        return self.allowed_image_types.split(",")


# Load settings from .env file
settings = Settings()
