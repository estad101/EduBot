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
        logger.info("Initializing database - importing models...")
        
        # Import models to register them with Base.metadata
        from models.student import Student
        logger.info("✓ Imported Student model")
        
        from models.lead import Lead
        logger.info("✓ Imported Lead model")
        
        from models.homework import Homework
        logger.info("✓ Imported Homework model")
        
        from models.payment import Payment
        logger.info("✓ Imported Payment model")
        
        from models.subscription import Subscription
        logger.info("✓ Imported Subscription model")
        
        from models.tutor import Tutor
        logger.info("✓ Imported Tutor model")
        
        from models.tutor_assignment import TutorAssignment
        logger.info("✓ Imported TutorAssignment model")
        
        logger.info(f"Creating tables with Base.metadata (tables: {list(Base.metadata.tables.keys())})")
        Base.metadata.create_all(bind=engine)
        logger.info("✓✓✓ DATABASE TABLES INITIALIZED SUCCESSFULLY ✓✓✓")
        
    except Exception as e:
        logger.error(f"❌ ERROR initializing database: {str(e)}", exc_info=True)
        # Don't raise - just log and continue
        # Tables will be created when first query succeeds


def drop_db():
    """Drop all tables (for testing only)."""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ Database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise

