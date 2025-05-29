from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class UserId:
    """User ID value object with UUID validation."""
    
    value: UUID
    
    def __post_init__(self) -> None:
        """Validate UUID after initialization."""
        # No need to check type, dataclass enforces UUID type
    
    def __str__(self) -> str:
        """String representation of user ID."""
        return str(self.value)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another UserId."""
        if not isinstance(other, UserId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.value)
    
    @classmethod
    def generate(cls) -> 'UserId':
        """Generate a new random UserId."""
        return cls(uuid4())
    
    @classmethod
    def from_string(cls, value: str) -> 'UserId':
        """Create UserId from string representation."""
        try:
            return cls(UUID(value))
        except ValueError as e:
            raise ValueError(f"Invalid UUID format: {value}") from e
    
    @classmethod
    def from_uuid(cls, value: UUID) -> 'UserId':
        """Create UserId from UUID object."""
        return cls(value)
    
    def to_uuid(self) -> UUID:
        """Convert to UUID object."""
        return self.value