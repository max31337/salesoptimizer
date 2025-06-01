from dataclasses import dataclass


@dataclass(frozen=True)
class UserStatus:
    """User status value object with business logic."""
    
    value: str
    
    # Status constants
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    
    _VALID_STATUSES = [PENDING, ACTIVE, INACTIVE, SUSPENDED]
    
    def __post_init__(self):
        if self.value not in self._VALID_STATUSES:
            raise ValueError(f"Invalid status: {self.value}")
    
    def is_active(self) -> bool:
        """Check if status allows user to be active."""
        return self.value == self.ACTIVE
    
    def can_login(self) -> bool:
        """Check if status allows login."""
        return self.value in [self.ACTIVE]
    
    def can_be_activated(self) -> bool:
        """Check if status can transition to active."""
        return self.value in [self.PENDING, self.INACTIVE]
    
    def can_be_suspended(self) -> bool:
        """Check if status can be suspended."""
        return self.value in [self.ACTIVE, self.INACTIVE]
    
    def requires_verification(self) -> bool:
        """Check if status requires email verification."""
        return self.value == self.PENDING
    
    def transition_to(self, new_status: 'UserStatus') -> 'UserStatus':
        """Validate and perform status transition."""
        valid_transitions = self._get_valid_transitions()
        
        if new_status.value not in valid_transitions[self.value]:
            raise ValueError(
                f"Invalid status transition from {self.value} to {new_status.value}"
            )
        
        return new_status
    
    @classmethod
    def pending(cls) -> 'UserStatus':
        """Create pending status."""
        return cls(cls.PENDING)
    
    @classmethod
    def active(cls) -> 'UserStatus':
        """Create active status."""
        return cls(cls.ACTIVE)
    
    @classmethod
    def inactive(cls) -> 'UserStatus':
        """Create inactive status."""
        return cls(cls.INACTIVE)
    
    @classmethod
    def suspended(cls) -> 'UserStatus':
        """Create suspended status."""
        return cls(cls.SUSPENDED)
    
    def _get_valid_transitions(self) -> dict[str, list[str]]:
        """Define valid status transitions."""
        return {
            self.PENDING: [self.ACTIVE, self.INACTIVE],
            self.ACTIVE: [self.INACTIVE, self.SUSPENDED],
            self.INACTIVE: [self.ACTIVE, self.SUSPENDED],
            self.SUSPENDED: [self.ACTIVE, self.INACTIVE]
        }