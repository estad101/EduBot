"""
Database configuration and session management - ASYNC VERSION with FALLBACK.
This provides full async/await support for non-blocking database operations.
Falls back to sync mode if aiomysql is not available.
"""
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import NullPool
from config.settings import settings
import logging
import sys

logger = logging.getLogger(__name__)

# Base class for all ORM models (define first, before any conditional imports)
Base = declarative_base()

# Initialize ASYNC_MODE flag
ASYNC_MODE = False

# Try to import async dependencies
try:
    # First, try to import aiomysql to ensure it's available
    import aiomysql
    
    from sqlalchemy.ext.asyncio import (
        create_async_engine,
        AsyncSession,
        async_sessionmaker,
    )
    from sqlalchemy import select, event, text
    ASYNC_MODE = True
    ASYNC_DRIVER = "aiomysql"
    logger.info("✓ Async mode enabled (aiomysql available)")
except ImportError as e:
    logger.warning(f"⚠ aiomysql not available, trying asyncmy fallback...")
    try:
        import asyncmy
        from sqlalchemy.ext.asyncio import (
            create_async_engine,
            AsyncSession,
            async_sessionmaker,
        )
        from sqlalchemy import select, event, text
        ASYNC_MODE = True
        ASYNC_DRIVER = "asyncmy"
        logger.info("✓ Async mode enabled (asyncmy available)")
    except ImportError:
        logger.warning("⚠ Async drivers not available - falling back to sync mode")
        ASYNC_MODE = False
        ASYNC_DRIVER = None

if ASYNC_MODE:
    # ASYNC MODE - Non-blocking database operations
    if ASYNC_DRIVER == "aiomysql":
        async_db_url = settings.database_url.replace(
            "mysql+pymysql://", "mysql+aiomysql://"
        ) if "mysql+pymysql://" in settings.database_url else settings.database_url.replace(
            "mysql://", "mysql+aiomysql://"
        )
    elif ASYNC_DRIVER == "asyncmy":
        async_db_url = settings.database_url.replace(
            "mysql+pymysql://", "mysql+asyncmy://"
        ) if "mysql+pymysql://" in settings.database_url else settings.database_url.replace(
            "mysql://", "mysql+asyncmy://"
        )
    else:
        async_db_url = settings.database_url

    try:
        logger.info(f"Creating ASYNC database engine with driver: {ASYNC_DRIVER}")
        engine = create_async_engine(
            async_db_url,
            poolclass=NullPool,
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

    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )

    async def get_db():
        """Async dependency injection for database session."""
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
            from models.bot_message import BotMessage
            logger.info("[OK] Imported BotMessage model")
            
            logger.info(f"\nStep 2: Creating tables (async)...")
            logger.info(f"Tables to create: {list(Base.metadata.tables.keys())}")
            
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(Base.metadata.create_all)
                
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

    # Also create a sync SessionLocal for backward compatibility
    # (used by some scripts and routes that need sync db access)
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    sync_engine = create_engine(
        settings.database_url,
        poolclass=NullPool,
        echo=settings.debug,
        connect_args={
            "charset": "utf8mb4",
            "use_unicode": True,
            "autocommit": True,
            "connect_timeout": 10,
        },
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

    def get_db_sync():
        """Synchronous database session for routes that need sync ORM queries."""
        db = SessionLocal()
        try:
            yield db
        except Exception as e:
            logger.error(f"Database session error: {e}")
            db.rollback()
            raise
        finally:
            db.close()

else:
    # SYNC FALLBACK MODE - Blocking database operations (compatibility mode)
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    logger.warning("=" * 80)
    logger.warning("DATABASE IN SYNC/FALLBACK MODE")
    logger.warning("Install aiomysql for async mode: pip install aiomysql")
    logger.warning("=" * 80)

    try:
        logger.info(f"Creating SYNC database engine (fallback mode)")
        engine = create_engine(
            settings.database_url,
            poolclass=NullPool,
            echo=settings.debug,
            connect_args={
                "charset": "utf8mb4",
                "use_unicode": True,
                "autocommit": True,
                "connect_timeout": 10,
            },
        )
        logger.info("✓ SYNC Database engine created successfully (compatibility mode)")
    except Exception as e:
        logger.error(f"✗ Failed to create sync database engine: {e}")
        raise

    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    def get_db():
        """Sync dependency injection for database session (compatibility mode)."""
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
        """Initialize database (create all tables) - SYNC FALLBACK VERSION."""
        try:
            logger.info("=" * 80)
            logger.info("STARTING SYNC DATABASE INITIALIZATION (Fallback Mode)")
            logger.info("=" * 80)
            
            logger.info("Step 1: Importing models...")
            
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
            from models.bot_message import BotMessage
            logger.info("[OK] Imported BotMessage model")
            
            logger.info(f"\nStep 2: Creating tables (sync fallback)...")
            logger.info(f"Tables to create: {list(Base.metadata.tables.keys())}")
            
            try:
                Base.metadata.create_all(bind=engine)
                
                logger.info("\nStep 3: Verifying table creation...")
                from sqlalchemy import inspect
                
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                if 'leads' in tables:
                    logger.info("[SUCCESS] LEADS TABLE CREATED SUCCESSFULLY")
                
                logger.info(f"All tables: {tables}")
                logger.info("=" * 80)
                logger.info("[SUCCESS] SYNC DATABASE INITIALIZATION COMPLETE (Fallback)")
                logger.info("=" * 80)
            except Exception as connection_error:
                logger.warning(f"[WARN] Could not connect to database during init: {str(connection_error)}")
                logger.warning("[WARN] Database operations will be retried on first use")
                logger.info("=" * 80)
            
        except Exception as e:
            logger.error("=" * 80)
            logger.error(f"❌ ERROR DURING SYNC DATABASE INITIALIZATION")
            logger.error(f"❌ {str(e)}")
            logger.error("=" * 80, exc_info=True)

    def drop_db():
        """Drop all tables (for testing only) - SYNC FALLBACK."""
        try:
            Base.metadata.drop_all(bind=engine)
            logger.info("✓ Database tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise


# Export the right get_db depending on mode
# This ensures admin routes always get sync sessions
__all__ = ['Base', 'engine', 'get_db', 'SessionLocal', 'ASYNC_MODE', 'init_db', 'drop_db', 'get_db_sync', 'async_session_maker']

# Provide get_db_sync for consistency across modes
if not ASYNC_MODE and 'get_db_sync' not in locals():
    get_db_sync = get_db

# In sync mode, provide a dummy async_session_maker for code that expects it
if not ASYNC_MODE:
    async_session_maker = None