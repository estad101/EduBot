"""
Database configuration and session management - ASYNC VERSION.
This provides full async/await support for non-blocking database operations.
"""
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncSession,
    async_sessionmaker,
)
from sqlalchemy import select, event, text
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

# Convert standard MySQL URL to async format
# mysql+pymysql://... -> mysql+aiomysql://...
async_db_url = settings.database_url.replace(
    "mysql+pymysql://", "mysql+aiomysql://"
) if "mysql+pymysql://" in settings.database_url else settings.database_url.replace(
    "mysql://", "mysql+aiomysql://"
)

# Create async database engine
try:
    logger.info(f"Creating ASYNC database engine")
    engine = create_async_engine(
        async_db_url,
        poolclass=NullPool,  # Don't pool connections on Railway
        echo=settings.debug,
        connect_args={
            "charset": "utf8mb4",
            "autocommit": True,
            "connect_timeout": 10,
        },
    )
    logger.info("✓ ASYNC Database engine created successfully")
except Exception as e:
    logger.error(f"✗ Failed to create async database engine: {e}")
    raise

# Create async session factory
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

# Base class for all ORM models
Base = declarative_base()


async def get_db():
    """Async dependency injection for database session.
    
    Usage in FastAPI:
        @app.get("/users")
        async def get_users(db: AsyncSession = Depends(get_db)):
            result = await db.execute(select(User))
            users = result.scalars().all()
            return users
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database (create all tables) - ASYNC VERSION."""
    try:
        logger.info("=" * 80)
        logger.info("STARTING ASYNC DATABASE INITIALIZATION")
        logger.info("=" * 80)
        
        logger.info("Step 1: Importing models...")
        
        # Import models to register them with Base.metadata
        from models.student import Student
        logger.info("[OK] Imported Student model")
        
        from models.lead import Lead
        logger.info("[OK] Imported Lead model")
        
        from models.homework import Homework
        logger.info("[OK] Imported Homework model")
        
        from models.payment import Payment
        logger.info("[OK] Imported Payment model")
        
        from models.subscription import Subscription
        logger.info("[OK] Imported Subscription model")
        
        from models.tutor import Tutor
        logger.info("[OK] Imported Tutor model")
        
        from models.tutor_assignment import TutorAssignment
        logger.info("[OK] Imported TutorAssignment model")
        
        from models.settings import AdminSetting
        logger.info("[OK] Imported AdminSetting model")
        
        from models.bot_message_template import BotMessageTemplate
        logger.info("[OK] Imported BotMessageTemplate model")
        
        logger.info(f"\nStep 2: Creating tables (async)...")
        logger.info(f"Tables to create: {list(Base.metadata.tables.keys())}")
        
        # Create all tables asynchronously
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            # Verify tables exist
            logger.info("\nStep 3: Verifying table creation...")
            async with engine.connect() as conn:
                result = await conn.execute(
                    text("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA = DATABASE()")
                )
                tables = [row[0] for row in result.fetchall()]
            
            if 'leads' in tables:
                logger.info("[SUCCESS] LEADS TABLE CREATED SUCCESSFULLY")
            
            logger.info(f"All tables: {tables}")
            logger.info("=" * 80)
            logger.info("[SUCCESS] ASYNC DATABASE INITIALIZATION COMPLETE")
            logger.info("=" * 80)
        except Exception as connection_error:
            logger.warning(f"[WARN] Could not connect to database during init: {str(connection_error)}")
            logger.warning("[WARN] Database operations will be retried on first use")
            logger.info("=" * 80)
        
    except Exception as e:
        logger.error("=" * 80)
        logger.error(f"❌ ERROR DURING ASYNC DATABASE INITIALIZATION")
        logger.error(f"❌ {str(e)}")
        logger.error("=" * 80, exc_info=True)


async def drop_db():
    """Drop all tables asynchronously (for testing only)."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        logger.info("✓ Database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


