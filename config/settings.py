"""
Application settings and configuration management.
Supports WhatsApp Cloud API directly (no n8n needed).
Optimized for Railway deployment.
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application configuration with Railway support."""

    # Database - Railway provides MYSQL_URL automatically
    database_url: str = os.getenv(
        "DATABASE_URL",
        os.getenv(
            "MYSQL_URL",
            "mysql+mysqlconnector://root:password@localhost:3306/edubot"
        )
    )

    # FastAPI
    debug: bool = os.getenv("DEBUG", "False").lower() == "true"
    api_title: str = os.getenv("API_TITLE", "EduBot API")
    api_version: str = os.getenv("API_VERSION", "1.0.0")
    api_port: int = int(os.getenv("API_PORT", "8000"))

    # Paystack (with safe defaults)
    paystack_public_key: str = os.getenv("PAYSTACK_PUBLIC_KEY", "pk_test_placeholder")
    paystack_secret_key: str = os.getenv("PAYSTACK_SECRET_KEY", "sk_test_placeholder")
    paystack_webhook_secret: str = os.getenv("PAYSTACK_WEBHOOK_SECRET", "webhook_placeholder")
    paystack_webhook_url: str = os.getenv(
        "PAYSTACK_WEBHOOK_URL",
        "http://localhost:8000/api/payments/webhook/paystack"
    )

    # WhatsApp (with safe defaults)
    whatsapp_api_key: str = os.getenv("WHATSAPP_API_KEY", "placeholder_api_key")
    whatsapp_phone_number_id: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "placeholder_phone_id")
    whatsapp_business_account_id: Optional[str] = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
    whatsapp_phone_number: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER")
    whatsapp_webhook_token: Optional[str] = os.getenv("WHATSAPP_WEBHOOK_TOKEN")

    # File Upload
    max_file_size_mb: int = int(os.getenv("MAX_FILE_SIZE_MB", "5"))
    allowed_image_types: str = os.getenv("ALLOWED_IMAGE_TYPES", "image/jpeg,image/png,image/webp")
    uploads_dir: str = os.getenv("UPLOADS_DIR", "uploads")

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    admin_origin: str = os.getenv("ADMIN_ORIGIN", "http://localhost:3000")
    allow_origins: str = os.getenv(
        "ALLOW_ORIGINS",
        "http://localhost:3000,http://localhost:8000,http://127.0.0.1:3000"
    )
    https_only: bool = os.getenv("HTTPS_ONLY", "False").lower() == "true"
    session_timeout_minutes: int = int(os.getenv("SESSION_TIMEOUT_MINUTES", "60"))
    rate_limit_per_minute: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/chatbot.log")

    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    sentry_dsn: Optional[str] = os.getenv("SENTRY_DSN")

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"

    @property
    def allowed_mime_types(self) -> list[str]:
        """Get allowed MIME types as list."""
        return [mime.strip() for mime in self.allowed_image_types.split(",")]


# Load settings
settings = Settings()
