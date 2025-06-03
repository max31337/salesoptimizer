from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Type, Any, List, AsyncGenerator
from infrastructure.config.settings import settings

# Create Base for models
Base = declarative_base()

def get_database_url():
    """Get database URL with proper configuration."""
    return settings.get_database_url()

# Use the helper function
database_url = get_database_url()
print(f"Connecting to database: {database_url}")

# Create sync engine
sync_engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.is_development  # Only echo in development
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
    """Test database connection."""
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
    sync_url = settings.get_database_url()
    return sync_url.replace("postgresql://", "postgresql+asyncpg://")

# Create async engine
async_engine = create_async_engine(
    get_async_database_url(),
    pool_pre_ping=True,
    pool_recycle=300,
    echo=settings.is_development
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

def register_models() -> List[Type[Any]]:
    """Register all models."""
    from infrastructure.db.models.user_model import UserModel
    from infrastructure.db.models.tenant_model import TenantModel
    from infrastructure.db.models.team_model import TeamModel
    
    return [UserModel, TenantModel, TeamModel]