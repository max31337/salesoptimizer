import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    """Application settings."""

    SECONDS_PER_DAY = 24 * 60 * 60
    
    # Environment
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Application URLs
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Database Configuration
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5432"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "salesoptimizer_db")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "postgres")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    INVITATION_TOKEN_EXPIRE_HOURS: int = int(os.getenv("INVITATION_TOKEN_EXPIRE_HOURS", "48"))

    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "sandbox.smtp.mailtrap.io")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "2525"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "false").lower() == "true"
    SMTP_USE_STARTTLS: bool = os.getenv("SMTP_USE_STARTTLS", "true").lower() == "true"
    
    # Email Defaults
    DEFAULT_FROM_EMAIL: str = os.getenv("DEFAULT_FROM_EMAIL", "noreply@salesoptimizer.com")
    DEFAULT_FROM_NAME: str = os.getenv("DEFAULT_FROM_NAME", "SalesOptimizer")
    
    # Security
    ALLOWED_HOSTS: List[str] = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
    
    # OAuth2 Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GITHUB_CLIENT_ID: str = os.getenv("GITHUB_CLIENT_ID", "")
    GITHUB_CLIENT_SECRET: str = os.getenv("GITHUB_CLIENT_SECRET", "")
    MICROSOFT_CLIENT_ID: str = os.getenv("MICROSOFT_CLIENT_ID", "")
    MICROSOFT_CLIENT_SECRET: str = os.getenv("MICROSOFT_CLIENT_SECRET", "")
    
    # OAuth Redirect URLs
    GOOGLE_OAUTH_REDIRECT_URL: str = os.getenv("GOOGLE_OAUTH_REDIRECT_URL", f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/v1/auth/oauth/google/callback")
    GITHUB_OAUTH_REDIRECT_URL: str = os.getenv("GITHUB_OAUTH_REDIRECT_URL", f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/v1/auth/oauth/github/callback")
    MICROSOFT_OAUTH_REDIRECT_URL: str = os.getenv("MICROSOFT_OAUTH_REDIRECT_URL", f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/v1/auth/oauth/microsoft/callback")
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() in ["development", "dev", "local"]
    
    @property
    def cookie_secure(self) -> bool:
        """Get secure cookie setting based on environment."""
        return self.is_production
    
    @property
    def cookie_samesite(self) -> str:
        """Get SameSite cookie setting based on environment."""
        return "none" if self.is_production else "lax"
    
    @property
    def cookie_domain(self) -> str:
        """Get cookie domain based on environment."""
        if self.is_production:
            # Extract domain from frontend URL for production
            from urllib.parse import urlparse
            parsed = urlparse(self.FRONTEND_URL)
            return parsed.hostname or "localhost"
        return "localhost"  # Use localhost for development
    
    def get_database_url(self) -> str:
        """Get database URL with proper configuration."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        if self.DATABASE_PASSWORD:
            return f"postgresql://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        else:
            return f"postgresql://{self.DATABASE_USER}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"

# Create a global settings instance
settings = Settings()