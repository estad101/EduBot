#!/usr/bin/env python3
"""
Create the leads table in the database.
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))

from config.database import engine
from models.lead import Lead
from utils.logger import get_logger

logger = get_logger("create_leads_table")

def main():
    """Create leads table."""
    try:
        logger.info("Creating leads table...")
        
        # Create all tables defined in models
        Lead.metadata.create_all(bind=engine)
        
        logger.info("✅ Leads table created successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Error creating table: {str(e)}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
