from dataclasses import dataclass
import re
from typing import ClassVar


@dataclass(frozen=True)
class Email:
    """Email value object with validation and normalization."""
    
    value: str
    
    EMAIL_REGEX: ClassVar[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    def __post_init__(self) -> None:
        """Validate and normalize email after initialization."""
        if not self.value:
            raise ValueError("Email cannot be empty")
        
        # Normalize email (lowercase and strip whitespace)
        normalized_email = self.value.lower().strip()
        
        if not re.match(self.EMAIL_REGEX, normalized_email):
            raise ValueError(f"Invalid email format: {self.value}")
        
        # Use object.__setattr__ because dataclass is frozen
        object.__setattr__(self, 'value', normalized_email)
    
    def __str__(self) -> str:
        """String representation of email."""
        return self.value
    
    @property
    def domain(self) -> str:
        """Get email domain part."""
        return self.value.split('@')[1]
    
    @property
    def local_part(self) -> str:
        """Get email local part (before @)."""
        return self.value.split('@')[0]
    
    @classmethod
    def from_string(cls, email_str: str) -> 'Email':
        """Create Email from string with validation."""
        return cls(email_str)
    
    def is_corporate_email(self) -> bool:
        """Check if email is from a corporate domain (not common free providers)."""
        free_providers = {
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'mail.com', 'protonmail.com'
        }
        return self.domain.lower() not in free_providers