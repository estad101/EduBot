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
try:
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
    
    # Test connection on startup
    with engine.connect() as conn:
        logger.info("✓ Database connection successful")
        
except Exception as e:
    logger.error(f"✗ Database connection failed: {e}")
    logger.warning("App will continue - database will be initialized on first use")
    # Fall back to a minimal engine that won't connect until needed
    engine = create_engine(
        settings.database_url,
        poolclass=NullPool,
        connect_args={
            "charset": "utf8mb4",
            "use_unicode": True,
            "autocommit": True,
        },
    )

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
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database tables: {e}")
        raise


def drop_db():
    """Drop all tables (for testing only)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ Database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

