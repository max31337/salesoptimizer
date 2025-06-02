"""Database models."""
from typing import List, Type, Any

# Import all models in the correct order to ensure proper registration
from .user_model import UserModel, GUID
from .tenant_model import TenantModel
from .team_model import TeamModel
from .invitation_model import InvitationModel

__all__ = [
    "UserModel",
    "TenantModel", 
    "TeamModel",
    "InvitationModel",
    "GUID"
]


def register_models() -> List[Type[Any]]:
    """Explicitly register all models with SQLAlchemy."""
    return [UserModel, TenantModel, TeamModel, InvitationModel]