# config/database.py - FIXED VERSION
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy import select, text 
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine
from config.settings import DATABASE_URL

# 1. Create async engine for FastAPI
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,  # Shows SQL queries in console
    pool_size=20,
    max_overflow=30,
)

# 2. Create sync engine for migrations
sync_database_url = DATABASE_URL.replace("postgresql+asyncpg", "postgresql")
sync_engine = create_engine(sync_database_url)

# 3. Create session factories
AsyncSessionLocal = sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

SyncSessionLocal = sessionmaker(sync_engine)

# 4. Create base class for all models
Base = declarative_base()

# 5. FIXED: Dependency to get database session
async def get_async_db():
    """Get database session - use as dependency in FastAPI"""
    db = AsyncSessionLocal()
    try:
        yield db
    finally:
        await db.close()

# For manual session management (used in startup)
def get_db_session():
    """Get a database session for manual use"""
    return AsyncSessionLocal()