import re
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TenantName:
    """Value object for tenant name."""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Tenant name cannot be empty")
        
        if not self.value.strip():
            raise ValueError("Tenant name cannot be only whitespace")
        
        if len(self.value.strip()) < 2:
            raise ValueError("Tenant name must be at least 2 characters")
        
        if len(self.value.strip()) > 100:
            raise ValueError("Tenant name must be less than 100 characters")
        
        # Update value to trimmed version
        object.__setattr__(self, 'value', self.value.strip())
    
    def to_slug(self) -> str:
        """Convert tenant name to URL-friendly slug."""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^\w\s-]', '', self.value.lower())
        slug = re.sub(r'[-\s]+', '-', slug)
        slug = slug.strip('-')
        
        if not slug:
            raise ValueError("Cannot create valid slug from tenant name")
        
        return slug
    
    def __str__(self) -> str:
        return self.value
    def __eq__(self, other: Any) -> bool:
        if isinstance(other, TenantName):
            return self.value.lower() == other.value.lower()
        if isinstance(other, str):
            return self.value.lower() == other.lower()
        return False
    
    def __hash__(self) -> int:
        return hash(self.value.lower())