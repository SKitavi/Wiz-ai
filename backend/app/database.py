from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import settings
from loguru import logger

# Create database engine
# For PostgreSQL, we add some optimization parameters
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=10,        # Number of connections to keep open
    max_overflow=20,     # Max connections above pool_size
    pool_recycle=3600,   # Recycle connections after 1 hour
    echo=False           # Set to True for SQL debugging
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class for all models
Base = declarative_base()

# Dependency for FastAPI routes
def get_db():
    """
    Database session dependency for FastAPI
    
    Usage in routes:
        @router.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Async session support (optional, for async endpoints)
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker

# For async operations, use asyncpg driver for PostgreSQL
async_database_url = settings.DATABASE_URL.replace(
    "postgresql://", 
    "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    async_database_url,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=False
)

AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_db():
    """
    Async database session dependency
    
    Usage:
        @router.get("/users")
        async def get_users(db: AsyncSession = Depends(get_async_db)):
            result = await db.execute(select(User))
            return result.scalars().all()
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


# Database initialization and health check
def init_db():
    """Initialize database tables"""
    try:
        # Import all models to register them with Base
        from app.models import User, Task, Plan, Document, ChatHistory
        
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


def check_db_connection():
    """Check if database connection is working"""
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


# Migration helper (for future use with Alembic)
def get_database_url():
    """Get database URL for Alembic migrations"""
    return settings.DATABASE_URL


if __name__ == "__main__":
    # Test database connection
    logger.info("Testing database connection...")
    
    if check_db_connection():
        logger.info("Initializing database...")
        init_db()
    else:
        logger.error("Cannot initialize database - connection failed")