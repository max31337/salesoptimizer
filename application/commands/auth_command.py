from dataclasses import dataclass


@dataclass(frozen=True)
class LoginCommand:
    """Command for user login."""
    
    email_or_username: str
    password: str
    
    def __post_init__(self) -> None:
        if not self.email_or_username or not self.email_or_username.strip():
            raise ValueError("Email or username is required")
        
        if not self.password or not self.password.strip():
            raise ValueError("Password is required")