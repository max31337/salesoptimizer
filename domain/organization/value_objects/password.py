from dataclasses import dataclass


@dataclass(frozen=True)
class Password:
    """Password value object with validation."""
    
    value: str
    
    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("Password cannot be empty")
        
        if len(self.value) < 8:
            raise ValueError("Password must be at least 8 characters long")
    
    def __str__(self) -> str:
        return self.value