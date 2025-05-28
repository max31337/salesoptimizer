import secrets
import string

def generate_jwt_secret(length: int = 64):
    """Generate a cryptographically secure JWT secret key."""
    # Use a mix of letters, digits, and special characters
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?"
    secret = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret

def generate_simple_secret(length: int = 64):
    """Generate a simple alphanumeric secret."""
    alphabet = string.ascii_letters + string.digits
    secret = ''.join(secrets.choice(alphabet) for _ in range(length))
    return secret

def generate_hex_secret(length: int = 32):
    """Generate a hex-based secret (64 characters for 32 bytes)."""
    return secrets.token_hex(length)

def generate_url_safe_secret(length: int = 64):
    """Generate a URL-safe base64 secret."""
    return secrets.token_urlsafe(length)

if __name__ == "__main__":
    print("=== JWT Secret Key Generators ===\n")
    
    print("1. Mixed characters (recommended for JWT):")
    print(f"   {generate_jwt_secret(64)}\n")
    
    print("2. Alphanumeric only:")
    print(f"   {generate_simple_secret(64)}\n")
    
    print("3. Hex format:")
    print(f"   {generate_hex_secret(32)}\n")
    
    print("4. URL-safe base64:")
    print(f"   {generate_url_safe_secret(64)}\n")
    
    print("Choose one of the above secrets for your JWT_SECRET_KEY")