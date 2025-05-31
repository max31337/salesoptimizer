import bcrypt
import secrets
import string

class PasswordService:
    """Service for password hashing and verification."""
    
    def __init__(self, rounds: int = 12) -> None:
        if rounds < 4 or rounds > 31:
            raise ValueError("Rounds must be between 4 and 31")
        self.rounds: int = rounds
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        if not password:
            raise ValueError("Password cannot be empty")
        
        salt: bytes = bcrypt.gensalt(rounds=self.rounds)
        hashed: bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        if not password or not hashed_password:
            return False
        
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
        except (ValueError, TypeError, AttributeError):
            return False
    
    def generate_temp_password(self, length: int = 12) -> str:
        """Generate a temporary password for new users."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(length))