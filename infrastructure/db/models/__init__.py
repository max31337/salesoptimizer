"""Database models."""
from typing import List, Type, Any

from .user_model import UserModel, GUID
from .tenant_model import TenantModel
from .team_model import TeamModel
from .invitation_model import InvitationModel
from .refresh_token_model import RefreshTokenModel
from .profile_update_request_model import ProfileUpdateRequestModel
from .activity_log_model import ActivityLogModel
from .sla_metric_model import SLAMetricModel
from .sla_threshold_model import SLAThresholdModel
from .sla_report_model import SLAReportModel
from .sla_alert_model import SLAAlertModel

__all__ = [
    "UserModel",
    "TenantModel", 
    "TeamModel",
    "InvitationModel",
    "RefreshTokenModel",
    "ProfileUpdateRequestModel",
    "ActivityLogModel",
    "SLAAlertModel",
    "SLAReportModel",
    "SLAThresholdModel",
    "SLAMetricModel",
    "GUID"
]


def register_models() -> List[Type[Any]]:
    """Explicitly register all models with SQLAlchemy."""
    return [UserModel, TenantModel, TeamModel, InvitationModel, RefreshTokenModel, ProfileUpdateRequestModel, ActivityLogModel, SLAAlertModel, SLAReportModel, SLAThresholdModel, SLAMetricModel]