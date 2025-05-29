"""Organization domain exceptions."""

from typing import Optional


class OrganizationDomainError(Exception):
    """Base exception for organization domain errors."""
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


# User-related exceptions
class UserError(OrganizationDomainError):
    """Base exception for user-related errors."""
    pass


class UserNotFoundError(UserError):
    """Raised when user is not found."""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        message = f"User with {identifier_type.lower()} '{identifier}' not found"
        super().__init__(message, "USER_NOT_FOUND")


class DuplicateUserError(UserError):
    """Raised when trying to create user with existing unique field."""
    
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        message = f"User with {field} '{value}' already exists"
        super().__init__(message, "DUPLICATE_USER")


class InvalidUserStatusError(UserError):
    """Raised when invalid user status operation is attempted."""
    
    def __init__(self, current_status: str, attempted_status: str):
        self.current_status = current_status
        self.attempted_status = attempted_status
        message = f"Cannot change user status from '{current_status}' to '{attempted_status}'"
        super().__init__(message, "INVALID_STATUS_TRANSITION")


class InvalidUserRoleError(UserError):
    """Raised when invalid user role is assigned."""
    
    def __init__(self, role: str):
        self.role = role
        message = f"Invalid user role: '{role}'"
        super().__init__(message, "INVALID_USER_ROLE")


class UserStatusTransitionError(UserError):
    """Raised when invalid status transition is attempted."""
    
    def __init__(self, from_status: str, to_status: str, reason: Optional[str] = None):
        self.from_status = from_status
        self.to_status = to_status
        self.reason = reason
        message = f"Cannot transition user status from '{from_status}' to '{to_status}'"
        if reason:
            message += f": {reason}"
        super().__init__(message, "USER_STATUS_TRANSITION_ERROR")


# Tenant-related exceptions
class TenantError(OrganizationDomainError):
    """Base exception for tenant-related errors."""
    pass


class TenantNotFoundError(TenantError):
    """Raised when tenant is not found."""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        message = f"Tenant with {identifier_type.lower()} '{identifier}' not found"
        super().__init__(message, "TENANT_NOT_FOUND")


class DuplicateTenantError(TenantError):
    """Raised when trying to create tenant with existing unique field."""
    
    def __init__(self, field: str, value: str):
        self.field = field
        self.value = value
        message = f"Tenant with {field} '{value}' already exists"
        super().__init__(message, "DUPLICATE_TENANT")


class TenantSlugConflictError(TenantError):
    """Raised when tenant slug already exists."""
    
    def __init__(self, slug: str):
        self.slug = slug
        message = f"Tenant with slug '{slug}' already exists"
        super().__init__(message, "TENANT_SLUG_CONFLICT")


class InvalidTenantStatusError(TenantError):
    """Raised when invalid tenant status operation is attempted."""
    
    def __init__(self, current_status: str, attempted_operation: str):
        self.current_status = current_status
        self.attempted_operation = attempted_operation
        message = f"Cannot {attempted_operation} tenant with status '{current_status}'"
        super().__init__(message, "INVALID_TENANT_STATUS")


# Team-related exceptions
class TeamError(OrganizationDomainError):
    """Base exception for team-related errors."""
    pass


class TeamNotFoundError(TeamError):
    """Raised when team is not found."""
    
    def __init__(self, identifier: str, identifier_type: str = "ID"):
        self.identifier = identifier
        self.identifier_type = identifier_type
        message = f"Team with {identifier_type.lower()} '{identifier}' not found"
        super().__init__(message, "TEAM_NOT_FOUND")


class DuplicateTeamError(TeamError):
    """Raised when trying to create team with existing name in tenant."""
    
    def __init__(self, name: str, tenant_id: str):
        self.name = name
        self.tenant_id = tenant_id
        message = f"Team with name '{name}' already exists in this organization"
        super().__init__(message, "DUPLICATE_TEAM")


class TeamCapacityExceededError(TeamError):
    """Raised when team capacity is exceeded."""
    
    def __init__(self, team_name: str, max_capacity: int, current_count: int):
        self.team_name = team_name
        self.max_capacity = max_capacity
        self.current_count = current_count
        message = f"Team '{team_name}' has reached maximum capacity ({max_capacity}/{max_capacity})"
        super().__init__(message, "TEAM_CAPACITY_EXCEEDED")


class InvalidTeamManagerError(TeamError):
    """Raised when invalid team manager is assigned."""
    
    def __init__(self, user_id: str, reason: str):
        self.user_id = user_id
        self.reason = reason
        message = f"Cannot assign user '{user_id}' as team manager: {reason}"
        super().__init__(message, "INVALID_TEAM_MANAGER")


class UserAlreadyInTeamError(TeamError):
    """Raised when trying to add user who is already in a team."""
    
    def __init__(self, user_id: str, current_team_id: str):
        self.user_id = user_id
        self.current_team_id = current_team_id
        message = f"User '{user_id}' is already a member of team '{current_team_id}'"
        super().__init__(message, "USER_ALREADY_IN_TEAM")


# Authentication and Authorization exceptions
class AuthenticationError(OrganizationDomainError):
    """Raised when authentication fails."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(OrganizationDomainError):
    """Raised when user doesn't have required permissions."""
    
    def __init__(self, user_id: str, required_permission: str, resource: Optional[str] = None):
        self.user_id = user_id
        self.required_permission = required_permission
        self.resource = resource
        
        message = f"User '{user_id}' lacks permission '{required_permission}'"
        if resource:
            message += f" for resource '{resource}'"
        
        super().__init__(message, "AUTHORIZATION_ERROR")


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""
    
    def __init__(self, email: Optional[str] = None):
        self.email = email
        message = "Invalid email or password"
        super().__init__(message)


class TokenExpiredError(AuthenticationError):
    """Raised when token has expired."""
    
    def __init__(self, token_type: str = "token"):
        self.token_type = token_type
        message = f"The {token_type} has expired"
        super().__init__(message)


class InvalidTokenError(AuthenticationError):
    """Raised when token is invalid or malformed."""
    
    def __init__(self, token_type: str = "token"):
        self.token_type = token_type
        message = f"Invalid {token_type}"
        super().__init__(message)


# Email and validation exceptions
class InvalidEmailError(OrganizationDomainError):
    """Raised when email format is invalid."""
    
    def __init__(self, email: str):
        self.email = email
        message = f"Invalid email format: '{email}'"
        super().__init__(message, "INVALID_EMAIL")


class EmailNotVerifiedError(OrganizationDomainError):
    """Raised when action requires verified email."""
    
    def __init__(self, email: str):
        self.email = email
        message = f"Email '{email}' is not verified"
        super().__init__(message, "EMAIL_NOT_VERIFIED")


# Invitation exceptions
class InvitationError(OrganizationDomainError):
    """Base exception for invitation-related errors."""
    pass


class InvalidInvitationTokenError(InvitationError):
    """Raised when invitation token is invalid or expired."""
    
    def __init__(self, reason: str = "Invalid or expired invitation token"):
        self.reason = reason
        super().__init__(reason, "INVALID_INVITATION_TOKEN")


class InvitationAlreadyUsedError(InvitationError):
    """Raised when invitation has already been used."""
    
    def __init__(self, email: str):
        self.email = email
        message = f"Invitation for '{email}' has already been used"
        super().__init__(message, "INVITATION_ALREADY_USED")


# Domain validation exceptions
class DomainValidationError(OrganizationDomainError):
    """Raised when domain validation fails."""
    
    def __init__(self, field: str, value: str, constraint: str):
        self.field = field
        self.value = value
        self.constraint = constraint
        message = f"Validation failed for field '{field}' with value '{value}': {constraint}"
        super().__init__(message, "DOMAIN_VALIDATION_ERROR")


class BusinessRuleViolationError(OrganizationDomainError):
    """Raised when business rule is violated."""
    
    def __init__(self, rule: str, context: Optional[str] = None):
        self.rule = rule
        self.context = context
        message = f"Business rule violation: {rule}"
        if context:
            message += f" (Context: {context})"
        super().__init__(message, "BUSINESS_RULE_VIOLATION")