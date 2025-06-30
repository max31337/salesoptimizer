"""Database models."""
from typing import List, Type, Any
# primary tables 
from .user_model import UserModel, GUID
from .tenant_model import TenantModel
from .team_model import TeamModel

# user related tables
from .oauth_provider_model import OAuthProviderModel
from .email_verification_model import EmailVerificationModel
from .login_activity_model import LoginActivityModel
from .activity_log_model import ActivityLogModel
from .profile_update_request_model import ProfileUpdateRequestModel
from .refresh_token_model import RefreshTokenModel
from .invitation_model import InvitationModel

# system related tables
from .sla_alert_model import SLAAlertModel
from .sla_metric_model import SLAMetricModel
from .sla_report_model import SLAReportModel
from .sla_threshold_model import SLAThresholdModel
from .uptime_event_model import UptimeEventModel

__all__ = [
    "GUID",
    "UserModel",
    "TenantModel",
    "TeamModel",
    "OAuthProviderModel",
    "EmailVerificationModel",
    "LoginActivityModel",
    "ActivityLogModel",
    "ProfileUpdateRequestModel",
    "RefreshTokenModel",
    "InvitationModel",
    "SLAAlertModel",
    "SLAMetricModel",
    "SLAReportModel",
    "SLAThresholdModel",
    "UptimeEventModel"
]


def register_models() -> List[Type[Any]]:
    """Explicitly register all models with SQLAlchemy."""
    return [GUID, UserModel, TenantModel, TeamModel, 
            OAuthProviderModel, EmailVerificationModel, 
            LoginActivityModel, ActivityLogModel, 
            ProfileUpdateRequestModel, RefreshTokenModel, 
            InvitationModel, SLAAlertModel, SLAMetricModel, 
            SLAReportModel, SLAThresholdModel, UptimeEventModel]