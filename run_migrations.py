#!/usr/bin/env python3
"""
Database migration script for Railway
Run migrations on the Railway-deployed database
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alembic.config import Config
from alembic import command

def run_migrations():
    """Run database migrations"""
    try:
        # Create alembic config
        alembic_cfg = Config("migrations/alembic.ini")
        
        # Get database URL from environment
        database_url = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")
        
        if not database_url:
            print("ERROR: DATABASE_URL or MYSQL_URL not set")
            return False
        
        print(f"Using database: {database_url[:50]}...")
        
        # Set sqlalchemy URL
        alembic_cfg.set_main_option("sqlalchemy.url", database_url)
        
        # Run upgrade
        print("Running migrations...")
        command.upgrade(alembic_cfg, "head")
        print("✓ Migrations completed successfully!")
        return True
        
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)
