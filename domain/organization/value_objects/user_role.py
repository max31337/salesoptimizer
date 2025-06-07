from dataclasses import dataclass
from typing import Set
from enum import Enum


class Permission(Enum):
    """System permissions."""    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    UPDATE_PROFILE = "update_profile"
    APPROVE_PROFILE_CHANGES = "approve_profile_changes"
    
    # Invitation Management
    CREATE_INVITATION = "create_invitation"
    VIEW_INVITATION = "view_invitation"
    MANAGE_INVITATION = "manage_invitation"
    
    # Tenant/Organization Management
    CREATE_TENANT = "create_tenant"
    MANAGE_TENANT = "manage_tenant"
    DELETE_TENANT = "delete_tenant"
    VIEW_ALL_TENANTS = "view_all_tenants"
    
    # Lead Management
    CREATE_LEAD = "create_lead"
    READ_LEAD = "read_lead"
    UPDATE_LEAD = "update_lead"
    DELETE_LEAD = "delete_lead"
    ASSIGN_LEAD = "assign_lead"
    
    # Team Management
    CREATE_TEAM = "create_team"
    MANAGE_TEAM = "manage_team"
    VIEW_TEAM_PERFORMANCE = "view_team_performance"
    
    # Organization (within tenant)
    MANAGE_ORGANIZATION = "manage_organization"
    VIEW_ANALYTICS = "view_analytics"
    EXPORT_DATA = "export_data"
    
    # System
    MANAGE_SYSTEM = "manage_system"
    VIEW_AUDIT_LOGS = "view_audit_logs"


@dataclass(frozen=True)
class UserRole:
    """User role value object with RBAC capabilities."""
    
    value: str
    
    # Role constants
    SUPER_ADMIN = "super_admin"
    ORG_ADMIN = "org_admin"
    SALES_MANAGER = "sales_manager"
    SALES_REP = "sales_rep"
    
    _VALID_ROLES = [SUPER_ADMIN, ORG_ADMIN, SALES_MANAGER, SALES_REP]
    
    def __post_init__(self):
        if self.value not in self._VALID_ROLES:
            raise ValueError(f"Invalid role: {self.value}")
    
    @property
    def permissions(self) -> Set[Permission]:
        """Get permissions for this role."""
        return self._get_role_permissions()[self.value]
    
    @property
    def hierarchy_level(self) -> int:
        """Get role hierarchy level (higher = more privileged)."""
        levels = {
            self.SUPER_ADMIN: 4,
            self.ORG_ADMIN: 3,
            self.SALES_MANAGER: 2,
            self.SALES_REP: 1
        }
        return levels[self.value]
    
    def is_super_admin(self) -> bool:
        """Check if this role is super admin."""
        return self.value == "super_admin"
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has specific permission."""
        return permission in self.permissions
    
    def can_create_invitations(self) -> bool:
        """Check if role can create invitations."""
        return self.has_permission(Permission.CREATE_INVITATION)
    
    def can_create_tenants(self) -> bool:
        """Check if role can create tenants."""
        return self.has_permission(Permission.CREATE_TENANT)
    
    def can_manage_invitations(self) -> bool:
        """Check if role can manage invitations."""
        return self.has_permission(Permission.MANAGE_INVITATION)
    
    def can_manage_role(self, other_role: 'UserRole') -> bool:
        """Check if this role can manage another role."""
        return self.hierarchy_level > other_role.hierarchy_level
    
    def can_access_resource(self, resource: str, action: str) -> bool:
        """Check if role can perform action on resource."""
        permission_key = f"{action}_{resource}".upper()
        try:
            permission = Permission(permission_key.lower())
            return self.has_permission(permission)
        except ValueError:
            return False
    
    @classmethod
    def super_admin(cls) -> 'UserRole':
        """Create super admin role."""
        return cls(cls.SUPER_ADMIN)
    
    @classmethod
    def org_admin(cls) -> 'UserRole':
        """Create org admin role."""
        return cls(cls.ORG_ADMIN)
    
    @classmethod
    def sales_manager(cls) -> 'UserRole':
        """Create sales manager role."""
        return cls(cls.SALES_MANAGER)
    
    @classmethod
    def sales_rep(cls) -> 'UserRole':
        """Create sales rep role."""
        return cls(cls.SALES_REP)
    
    def _get_role_permissions(self) -> dict[str, Set[Permission]]:
        """Define permissions for each role."""
        return {            self.SUPER_ADMIN: {
                # All permissions including tenant management
                Permission.MANAGE_SYSTEM,
                Permission.VIEW_AUDIT_LOGS,
                Permission.CREATE_TENANT, Permission.MANAGE_TENANT, 
                Permission.DELETE_TENANT, Permission.VIEW_ALL_TENANTS,  # Tenant management permissions
                Permission.MANAGE_ORGANIZATION,
                Permission.CREATE_USER, Permission.READ_USER, 
                Permission.UPDATE_USER, Permission.DELETE_USER,
                Permission.UPDATE_PROFILE, Permission.APPROVE_PROFILE_CHANGES,
                Permission.CREATE_INVITATION, Permission.VIEW_INVITATION, Permission.MANAGE_INVITATION,
                Permission.CREATE_TEAM, Permission.MANAGE_TEAM,
                Permission.VIEW_TEAM_PERFORMANCE,
                Permission.CREATE_LEAD, Permission.READ_LEAD,
                Permission.UPDATE_LEAD, Permission.DELETE_LEAD,
                Permission.ASSIGN_LEAD,
                Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            },
            
            self.ORG_ADMIN: {
                Permission.MANAGE_ORGANIZATION,  # Can manage their own organization settings
                Permission.CREATE_USER, Permission.READ_USER,
                Permission.UPDATE_USER, Permission.DELETE_USER,
                Permission.VIEW_INVITATION, Permission.MANAGE_INVITATION,  # Can manage invitations within their org
                Permission.CREATE_TEAM, Permission.MANAGE_TEAM,
                Permission.VIEW_TEAM_PERFORMANCE,
                Permission.CREATE_LEAD, Permission.READ_LEAD,
                Permission.UPDATE_LEAD, Permission.DELETE_LEAD,
                Permission.ASSIGN_LEAD,
                Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            },
            
            self.SALES_MANAGER: {
                Permission.READ_USER, Permission.UPDATE_USER,
                Permission.VIEW_INVITATION,  # Can only view invitations
                Permission.MANAGE_TEAM, Permission.VIEW_TEAM_PERFORMANCE,
                Permission.CREATE_LEAD, Permission.READ_LEAD,
                Permission.UPDATE_LEAD, Permission.DELETE_LEAD,
                Permission.ASSIGN_LEAD,
                Permission.VIEW_ANALYTICS,
            },
            
            self.SALES_REP: {
                Permission.READ_USER,
                Permission.CREATE_LEAD, Permission.READ_LEAD,
                Permission.UPDATE_LEAD,
            }
        }