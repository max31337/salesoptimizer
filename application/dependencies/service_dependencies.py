from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.db.base import get_db
from application.services.application_service import ApplicationService


def get_application_service(
    db: Annotated[Session, Depends(get_db)]
) -> ApplicationService:
    """Dependency to get application service with database session."""
    return ApplicationService(db)