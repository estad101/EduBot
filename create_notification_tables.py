#!/usr/bin/env python3
"""Create notification tables in database."""

import sys
import logging
from config.database import Base, engine
from models.notification import Notification, NotificationPreference

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_tables():
    """Create notification tables."""
    try:
        logger.info("Creating notification tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✓ Notification tables created successfully!")
        logger.info("  - notifications")
        logger.info("  - notification_preferences")
        return True
        
    except Exception as e:
        logger.error(f"Error creating tables: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_tables()
    sys.exit(0 if success else 1)
