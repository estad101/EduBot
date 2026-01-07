"""
Settings Service - Manages application configuration from database.

This service handles loading and caching WhatsApp and other settings
from the database, with fallback to environment variables.
"""
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from models.settings import AdminSetting
from config.settings import settings as env_settings

logger = logging.getLogger(__name__)

# In-memory cache for settings to avoid repeated database queries
_settings_cache: Dict[str, str] = {}
_cache_initialized = False


def init_settings_from_db(db: Session) -> bool:
    """
    Initialize settings cache from database.
    Called at application startup.
    
    This function:
    1. Loads all settings from database into memory cache
    2. Seeds database with environment variables if settings are empty
    3. Returns whether initialization was successful
    """
    global _settings_cache, _cache_initialized
    
    try:
        # Check if database has settings
        existing_settings = db.query(AdminSetting).filter(
            AdminSetting.key.in_([
                "whatsapp_api_key",
                "whatsapp_phone_number_id",
                "whatsapp_business_account_id",
                "whatsapp_phone_number"
            ])
        ).all()
        
        # If no settings in database, seed them from environment variables
        if not existing_settings or len(existing_settings) < 2:
            logger.info("Seeding WhatsApp settings from environment variables...")
            
            settings_to_seed = [
                ("whatsapp_api_key", env_settings.whatsapp_api_key, "WhatsApp API Access Token"),
                ("whatsapp_phone_number_id", env_settings.whatsapp_phone_number_id, "WhatsApp Phone Number ID"),
                ("whatsapp_business_account_id", env_settings.whatsapp_business_account_id, "WhatsApp Business Account ID"),
                ("whatsapp_phone_number", env_settings.whatsapp_phone_number, "WhatsApp Phone Number"),
                ("whatsapp_webhook_token", env_settings.whatsapp_webhook_token, "WhatsApp Webhook Verification Token"),
                ("paystack_public_key", env_settings.paystack_public_key, "Paystack Public Key"),
                ("paystack_secret_key", env_settings.paystack_secret_key, "Paystack Secret Key"),
                ("paystack_webhook_secret", env_settings.paystack_webhook_secret, "Paystack Webhook Secret"),
            ]
            
            seeded_count = 0
            for key, value, description in settings_to_seed:
                if value:  # Only seed if value exists in env vars
                    existing = db.query(AdminSetting).filter(AdminSetting.key == key).first()
                    if not existing:
                        setting = AdminSetting(
                            key=key,
                            value=value,
                            description=description
                        )
                        db.add(setting)
                        seeded_count += 1
            
            if seeded_count > 0:
                db.commit()
                logger.info(f"✓ Seeded {seeded_count} settings from environment variables")
        
        # Load all settings from database into cache
        all_settings = db.query(AdminSetting).all()
        for setting in all_settings:
            if setting.value:
                _settings_cache[setting.key] = setting.value
        
        _cache_initialized = True
        logger.info(f"✓ Settings cache initialized with {len(_settings_cache)} entries")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error initializing settings from database: {str(e)}")
        # Fall back to environment variables
        _cache_initialized = True
        return False


def get_setting(key: str, default: Optional[str] = None, db: Session = None) -> Optional[str]:
    """
    Get a setting value from cache or database.
    
    Args:
        key: Setting key
        default: Default value if setting not found
        db: Database session (optional, for fallback queries)
    
    Returns:
        Setting value or default
    """
    # Try cache first
    if key in _settings_cache:
        return _settings_cache[key]
    
    # Try environment variable fallback
    env_value = getattr(env_settings, key, None)
    if env_value:
        _settings_cache[key] = env_value
        return env_value
    
    # Try database if session provided
    if db:
        try:
            setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
            if setting and setting.value:
                _settings_cache[key] = setting.value
                return setting.value
        except Exception as e:
            logger.warning(f"Error querying setting '{key}' from database: {str(e)}")
    
    return default


def update_setting(key: str, value: str, description: str = None, db: Session = None) -> bool:
    """
    Update or create a setting in the database.
    
    Args:
        key: Setting key
        value: Setting value
        description: Setting description (optional)
        db: Database session (required)
    
    Returns:
        True if successful, False otherwise
    """
    if not db:
        logger.error("Database session required to update setting")
        return False
    
    try:
        setting = db.query(AdminSetting).filter(AdminSetting.key == key).first()
        
        if setting:
            setting.value = value
        else:
            setting = AdminSetting(
                key=key,
                value=value,
                description=description or f"Setting for {key}"
            )
            db.add(setting)
        
        db.commit()
        
        # Update cache
        _settings_cache[key] = value
        
        logger.info(f"✓ Setting '{key}' updated successfully")
        return True
        
    except Exception as e:
        logger.error(f"✗ Error updating setting '{key}': {str(e)}")
        db.rollback()
        return False


def get_whatsapp_config(db: Session = None) -> Dict[str, Optional[str]]:
    """
    Get complete WhatsApp configuration.
    
    Returns a dictionary with WhatsApp API token, phone number ID, 
    business account ID, and phone number.
    """
    return {
        "api_key": get_setting("whatsapp_api_key", env_settings.whatsapp_api_key, db),
        "phone_number_id": get_setting("whatsapp_phone_number_id", env_settings.whatsapp_phone_number_id, db),
        "business_account_id": get_setting("whatsapp_business_account_id", env_settings.whatsapp_business_account_id, db),
        "phone_number": get_setting("whatsapp_phone_number", env_settings.whatsapp_phone_number, db),
        "webhook_token": get_setting("whatsapp_webhook_token", env_settings.whatsapp_webhook_token, db),
    }


def get_paystack_config(db: Session = None) -> Dict[str, Optional[str]]:
    """
    Get complete Paystack configuration.
    
    Returns a dictionary with Paystack public key, secret key, and webhook secret.
    """
    return {
        "public_key": get_setting("paystack_public_key", env_settings.paystack_public_key, db),
        "secret_key": get_setting("paystack_secret_key", env_settings.paystack_secret_key, db),
        "webhook_secret": get_setting("paystack_webhook_secret", env_settings.paystack_webhook_secret, db),
    }


def refresh_cache(db: Session) -> bool:
    """
    Refresh the settings cache from database.
    Useful after updating settings to ensure fresh values.
    """
    global _settings_cache, _cache_initialized
    
    try:
        _settings_cache.clear()
        all_settings = db.query(AdminSetting).all()
        for setting in all_settings:
            if setting.value:
                _settings_cache[setting.key] = setting.value
        
        logger.info(f"✓ Settings cache refreshed with {len(_settings_cache)} entries")
        return True
    except Exception as e:
        logger.error(f"✗ Error refreshing settings cache: {str(e)}")
        return False
