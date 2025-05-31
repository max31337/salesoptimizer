from typing import Final
import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Email:
    """Email value object with validation."""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Email cannot be empty")
        
        # Basic email validation
        email_pattern: Final[str] = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, self.value):
            raise ValueError("Invalid email format")
    
    def __str__(self) -> str:
        return self.value