"""Authentication related exceptions."""


class AuthenticationError(Exception):
    """Raised when authentication fails."""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class AuthorizationError(Exception):
    """Raised when authorization fails."""
    
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(self.message)


class InvalidCredentialsError(AuthenticationError):
    """Raised when user credentials are invalid."""
    
    def __init__(self) -> None:
        super().__init__("Invalid credentials")


class UserNotFoundError(AuthenticationError):
    """Raised when user is not found."""
    
    def __init__(self) -> None:
        super().__init__("User not found")


class InactiveUserError(AuthenticationError):
    """Raised when user account is not active."""
    
    def __init__(self) -> None:
        super().__init__("Account is not active")