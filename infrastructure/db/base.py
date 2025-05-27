import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv()

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

engine = create_engine(
    database_url,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    Base.metadata.create_all(bind=engine)

def test_connection():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            print("✅ Database connection successful!")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False