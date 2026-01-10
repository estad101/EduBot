#!/usr/bin/env python
"""
Seed script to ensure bot_name exists in admin_settings table.
This ensures the login page can fetch the bot name from the database.
"""
from config.database import SessionLocal
from models.settings import AdminSetting
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def seed_bot_name():
    """Seed default bot_name setting if it doesn't exist."""
    db = SessionLocal()
    try:
        # Check if bot_name setting exists
        existing_setting = db.query(AdminSetting).filter(
            AdminSetting.key == "bot_name"
        ).first()

        if not existing_setting:
            # Create new bot_name setting
            bot_name_setting = AdminSetting(
                key="bot_name",
                value="EduBot",
                description="Name of the bot used in UI"
            )
            db.add(bot_name_setting)
            db.commit()
            logger.info("✓ Created bot_name setting in admin_settings table: 'EduBot'")
        else:
            logger.info(f"✓ bot_name setting already exists: '{existing_setting.value}'")

        # List all current settings
        all_settings = db.query(AdminSetting).all()
        logger.info("\n" + "=" * 60)
        logger.info("Current admin_settings table contents:")
        logger.info("=" * 60)
        for setting in all_settings:
            display_value = setting.value[:50] + "..." if setting.value and len(setting.value) > 50 else setting.value
            logger.info(f"  {setting.key:40} = {display_value}")
        logger.info("=" * 60 + "\n")

    except Exception as e:
        logger.error(f"Error seeding bot_name: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("Seeding bot_name to admin_settings table...")
    seed_bot_name()
    logger.info("Done!")
