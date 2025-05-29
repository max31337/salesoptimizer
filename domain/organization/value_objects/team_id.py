from dataclasses import dataclass
from uuid import UUID, uuid4


@dataclass(frozen=True)
class TeamId:
    """Team ID value object with UUID validation."""
    
    value: UUID
    
    def __post_init__(self) -> None:
        """Validate UUID after initialization."""
        pass
    
    def __str__(self) -> str:
        """String representation of team ID."""
        return str(self.value)
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another TeamId."""
        if not isinstance(other, TeamId):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        """Hash for use in sets and dictionaries."""
        return hash(self.value)
    
    @classmethod
    def generate(cls) -> 'TeamId':
        """Generate a new random TeamId."""
        return cls(uuid4())
    
    @classmethod
    def from_string(cls, value: str) -> 'TeamId':
        """Create TeamId from string representation."""
        try:
            return cls(UUID(value))
        except ValueError as e:
            raise ValueError(f"Invalid UUID format: {value}") from e
    
    @classmethod
    def from_uuid(cls, value: UUID) -> 'TeamId':
        """Create TeamId from UUID object."""
        return cls(value)
    
    def to_uuid(self) -> UUID:
        """Convert to UUID object."""
        return self.value