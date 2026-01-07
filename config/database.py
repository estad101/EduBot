"""
Database configuration and session management.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool, NullPool
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Create database engine with improved connection handling
# Use NullPool for Railway to avoid connection pooling issues
# Railway's MySQL service has its own connection management
engine = create_engine(
    settings.database_url,
    poolclass=NullPool,  # Don't pool connections on Railway
    echo=settings.debug,
    connect_args={
        "charset": "utf8mb4",
        "use_unicode": True,
        "autocommit": True,
        "connect_timeout": 10,
    },
)

# Don't test connection at startup - it will fail if database is offline
# Connection will be established when first query is made
logger.info("Database engine created (lazy connection - will connect on first use)")

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all ORM models
Base = declarative_base()


def get_db():
    """Dependency injection for database session."""
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db():
    """Initialize database (create all tables)."""
    try:
        logger.info("=" * 80)
        logger.info("STARTING DATABASE INITIALIZATION")
        logger.info("=" * 80)
        
        logger.info("Step 1: Importing models...")
        
        # Import all models from models package to register them with Base.metadata
        import models
        logger.info(f"✓ Imported models package with {len(Base.metadata.tables)} tables registered")
        
        logger.info(f"\nStep 2: Creating tables...")
        logger.info(f"Tables to create: {list(Base.metadata.tables.keys())}")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        # Verify leads table exists
        logger.info("\nStep 3: Verifying table creation...")
        from sqlalchemy import inspect, text
        
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'leads' in tables:
            logger.info("✓✓✓ LEADS TABLE CREATED SUCCESSFULLY ✓✓✓")
            leads_columns = [col['name'] for col in inspector.get_columns('leads')]
            logger.info(f"Leads table columns: {leads_columns}")
        else:
            logger.warning(f"⚠ Leads table NOT FOUND. Available tables: {tables}")
        
        logger.info("=" * 80)
        logger.info("✓✓✓ DATABASE INITIALIZATION COMPLETE ✓✓✓")
        logger.info("=" * 80)
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR DURING DATABASE INITIALIZATION")
        logger.error(f"❌ {str(e)}")
        logger.error("=" * 80, exc_info=True)


def drop_db():
    """Drop all tables (for testing only)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ Database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

