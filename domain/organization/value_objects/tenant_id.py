from dataclasses import dataclass
import uuid

@dataclass(frozen=True)
class TenantId:
    """Value object representing a tenant identifier."""
    
    value: uuid.UUID
    
    def __post_init__(self):
        pass
    
    @classmethod
    def generate(cls) -> 'TenantId':
        """Generate a new unique TenantId."""
        return cls(uuid.uuid4())
    
    @classmethod
    def from_string(cls, value: str) -> 'TenantId':
        """Create TenantId from string value."""
        return cls(uuid.UUID(value))
    
    def __str__(self) -> str:
        return str(self.value)
    
    def __repr__(self) -> str:
        return f"TenantId('{self.value}')"
