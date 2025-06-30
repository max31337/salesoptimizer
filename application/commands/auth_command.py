from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    """Command for user login."""
    email_or_username: str
    password: str
    user_agent: str = ""
    ip_address: str = ""
    
    def __post_init__(self) -> None:
        if not self.email_or_username or not self.email_or_username.strip():
            raise ValueError("Email or username is required")
        if not self.password or not self.password.strip():
            raise ValueError("Password is required")


@dataclass(frozen=True)
class SignupCommand:
    """Command for self-serve user signup."""
    
    first_name: str
    last_name: str
    email: str
    password: str
    organization_name: str
    subscription_tier: str = "free"
    
    def __post_init__(self) -> None:
        # Validate required fields
        required_fields = [
            ("first_name", self.first_name),
            ("last_name", self.last_name),
            ("email", self.email),
            ("password", self.password),
            ("organization_name", self.organization_name)
        ]
        
        for field_name, field_value in required_fields:
            if not field_value or not field_value.strip():
                raise ValueError(f"{field_name.replace('_', ' ').title()} is required")
        
        # Validate password strength
        if len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Validate subscription tier
        if self.subscription_tier not in ["free", "basic", "pro"]:
            raise ValueError("Invalid subscription tier")