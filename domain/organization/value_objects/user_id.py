from uuid import UUID, uuid4
from dataclasses import dataclass


@dataclass(frozen=True)
class UserId:
    """User ID value object."""
    
    value: UUID
    
    def __post_init__(self) -> None:
        pass
    
    @classmethod
    def generate(cls) -> 'UserId':
        """Generate a new user ID."""
        return cls(uuid4())
    
    @classmethod
    def from_string(cls, value: str) -> 'UserId':
        """Create user ID from string."""
        try:
            return cls(UUID(value))
        except ValueError:
            raise ValueError("Invalid UUID format")
    
    def __str__(self) -> str:
        return str(self.value)