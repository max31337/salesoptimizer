from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.base import get_async_db
from application.services.application_service import ApplicationService


async def get_application_service(
    db: Annotated[AsyncSession, Depends(get_async_db)]
) -> ApplicationService:
    """Dependency to get application service with async database session."""
    return ApplicationService(db)  # Only pass the database session