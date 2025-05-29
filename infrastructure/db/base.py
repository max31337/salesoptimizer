import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from dotenv import load_dotenv
from typing import Type, Any, List


load_dotenv()

# Create Base for models
Base = declarative_base()

def get_database_url():
    """Get database URL with proper configuration."""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        DATABASE_HOST = os.getenv("DATABASE_HOST", "localhost")
        DATABASE_PORT = os.getenv("DATABASE_PORT", "5432")
        DATABASE_NAME = os.getenv("DATABASE_NAME", "salesoptimizer_db")
        DATABASE_USER = os.getenv("DATABASE_USER")
        DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")
        
        if DATABASE_PASSWORD:
            database_url = f"postgresql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
        else:
            database_url = f"postgresql://{DATABASE_USER}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    else:
        database_url = DATABASE_URL
    
    return database_url

# Use the helper function
database_url = get_database_url()
print(f"Connecting to database: {database_url}")

# Create sync engine
sync_engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=sync_engine)

def test_connection():
    try:
        with sync_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

# Async database setup
def get_async_database_url() -> str:
    """Get async database URL."""
    url = get_database_url()
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://")
    return url

# Create async engine
async_engine = create_async_engine(get_async_database_url(), echo=False)
AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)

from typing import AsyncGenerator

async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """Get async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


def register_models() -> List[Type[Any]]:
    """Register all models."""
    from infrastructure.db.models.user_model import UserModel
    from infrastructure.db.models.tenant_model import TenantModel
    from infrastructure.db.models.team_model import TeamModel
    
    return [UserModel, TenantModel, TeamModel]