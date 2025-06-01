from dataclasses import dataclass
from typing import Set
from enum import Enum


class Permission(Enum):
    """System permissions."""
    # User Management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
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
    
    # Organization
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
    
    def has_permission(self, permission: Permission) -> bool:
        """Check if role has specific permission."""
        return permission in self.permissions
    
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
        return {
            self.SUPER_ADMIN: {
                # All permissions
                Permission.MANAGE_SYSTEM,
                Permission.VIEW_AUDIT_LOGS,
                Permission.MANAGE_ORGANIZATION,
                Permission.CREATE_USER, Permission.READ_USER, 
                Permission.UPDATE_USER, Permission.DELETE_USER,
                Permission.CREATE_TEAM, Permission.MANAGE_TEAM,
                Permission.VIEW_TEAM_PERFORMANCE,
                Permission.CREATE_LEAD, Permission.READ_LEAD,
                Permission.UPDATE_LEAD, Permission.DELETE_LEAD,
                Permission.ASSIGN_LEAD,
                Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            },
            
            self.ORG_ADMIN: {
                Permission.MANAGE_ORGANIZATION,
                Permission.CREATE_USER, Permission.READ_USER,
                Permission.UPDATE_USER, Permission.DELETE_USER,
                Permission.CREATE_TEAM, Permission.MANAGE_TEAM,
                Permission.VIEW_TEAM_PERFORMANCE,
                Permission.CREATE_LEAD, Permission.READ_LEAD,
                Permission.UPDATE_LEAD, Permission.DELETE_LEAD,
                Permission.ASSIGN_LEAD,
                Permission.VIEW_ANALYTICS, Permission.EXPORT_DATA,
            },
            
            self.SALES_MANAGER: {
                Permission.READ_USER, Permission.UPDATE_USER,
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