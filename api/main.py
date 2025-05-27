from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from infrastructure.db.base import get_db, test_connection, create_tables
from contextlib import asynccontextmanager
from api.routes import users

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Testing database connection...")
    if test_connection():
        print("✅ Database connection successful!")
        create_tables()
        print("✅ Database tables created/verified!")
    else:
        print("❌ Database connection failed!")
    yield

app = FastAPI(title="Sales Optimizer CRM", version="1.0.0", lifespan=lifespan)


app.include_router(users.router, prefix="/api/v1")

@app.get("/")
def root():
    return {"message": "Hello from Sales Optimizer CRM"}

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    return {"status": "healthy", "database": "connected"}
