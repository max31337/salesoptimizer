from dataclasses import dataclass
import secrets
import string


@dataclass(frozen=True)
class InvitationToken:
    """Value object for invitation tokens."""
    
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Invitation token cannot be empty")
        if len(self.value) < 32:
            raise ValueError("Invitation token must be at least 32 characters")
    
    @classmethod
    def generate(cls) -> 'InvitationToken':
        """Generate a secure random invitation token."""
        # Use URL-safe characters for tokens that might go in URLs
        alphabet = string.ascii_letters + string.digits + '-_'
        token = ''.join(secrets.choice(alphabet) for _ in range(64))
        return cls(token)
    
    def __str__(self) -> str:
        return self.value
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InvitationToken):
            return False
        return self.value == other.value
    
    def __hash__(self) -> int:
        return hash(self.value)