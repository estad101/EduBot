"""
Application settings and configuration management.
Supports WhatsApp Cloud API directly (no n8n needed)."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration."""

    # Database
    database_url: str = "mysql+mysqlconnector://payroll_user:password@localhost:3306/whatsapp_chatbot"

    # FastAPI
    debug: bool = False
    api_title: str = "EduBot API"
    api_version: str = "1.0.0"
    api_port: int = 8000

    # Paystack (with defaults to prevent startup errors)
    paystack_public_key: str = "pk_test_placeholder"
    paystack_secret_key: str = "sk_test_placeholder"
    paystack_webhook_secret: str = "webhook_secret_placeholder"
    paystack_webhook_url: Optional[str] = "http://localhost:8000/api/payments/webhook/paystack"

    # WhatsApp (with defaults)
    whatsapp_api_key: str = "placeholder_api_key"
    whatsapp_phone_number_id: str = "placeholder_phone_id"
    whatsapp_business_account_id: Optional[str] = None
    whatsapp_phone_number: Optional[str] = None
    whatsapp_webhook_token: Optional[str] = None  # For webhook verification

    # File Upload
    max_file_size_mb: int = 5
    allowed_image_types: str = "image/jpeg,image/png,image/webp"
    uploads_dir: str = "uploads"

    # Security
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    admin_origin: str = "http://localhost:3000"
    allow_origins: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000"
    https_only: bool = False
    session_timeout_minutes: int = 60
    rate_limit_per_minute: int = 60

    # Logging
    log_level: str = "INFO"
    log_file: str = "logs/chatbot.log"

    # Environment
    environment: str = "development"    # Monitoring & Error Tracking
    sentry_dsn: Optional[str] = None  # Sentry error tracking DSN
    environment: str = "development"  # production, staging, development

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields from .env

    @property
    def allowed_mime_types(self) -> list[str]:
        """Get allowed MIME types as list."""
        return self.allowed_image_types.split(",")


# Load settings from .env file
settings = Settings()
