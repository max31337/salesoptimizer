from authlib.integrations.starlette_client import OAuth  # type: ignore
from fastapi import FastAPI
import os
from urllib.parse import urljoin
from typing import Dict
from typing import TypedDict
from pydantic_settings import BaseSettings
from typing import Any

from infrastructure.config.settings import settings

class ProviderConfig(TypedDict):
    client_id: str
    client_secret: str
    redirect_uri: str

oauth: OAuth = OAuth()

def setup_oauth(app: FastAPI) -> OAuth:
    """Setup OAuth configuration."""    
    # Google OAuth
    oauth.register(  # type: ignore
        name='google',
        client_id=os.getenv('GOOGLE_CLIENT_ID'),
        client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid_configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )
    
    # GitHub OAuth
    oauth.register(  # type: ignore
        name='github',
        client_id=os.getenv('GITHUB_CLIENT_ID'),
        client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
        api_base_url='https://api.github.com/',
        client_kwargs={'scope': 'user:email'},
    )
    
    return oauth


def get_oauth_config() -> Dict[str, ProviderConfig]:
    """Get OAuth configuration with validation."""
    base_url = os.getenv('BASE_URL', 'http://localhost:8000')
    
    config: Dict[str, ProviderConfig] = {
        'google': {
            'client_id': os.getenv('GOOGLE_CLIENT_ID', ''),
            'client_secret': os.getenv('GOOGLE_CLIENT_SECRET', ''),
            'redirect_uri': urljoin(base_url, '/api/v1/auth/google/callback')
        },
        'github': {
            'client_id': os.getenv('GITHUB_CLIENT_ID', ''),
            'client_secret': os.getenv('GITHUB_CLIENT_SECRET', ''),
            'redirect_uri': urljoin(base_url, '/api/v1/auth/github/callback')
        }
    }
    
    # Validate required configs
    for provider, settings in config.items():
        if not settings['client_id'] or not settings['client_secret']:
            raise ValueError(f"Missing OAuth configuration for {provider}")
    
    return config


class OAuthConfig(BaseSettings):
    """OAuth configuration settings."""
    
    google_client_id: str = settings.GOOGLE_CLIENT_ID
    google_client_secret: str = settings.GOOGLE_CLIENT_SECRET
    google_redirect_url: str = settings.GOOGLE_OAUTH_REDIRECT_URL

    github_client_id: str = ""
    github_client_secret: str = ""
    microsoft_client_id: str = ""
    microsoft_client_secret: str = ""
    
    # Provider-specific redirect URLs
    google_oauth_redirect_url: str = "http://localhost:8000/api/v1/auth/oauth/google/callback"
    github_oauth_redirect_url: str = "http://localhost:8000/api/v1/auth/oauth/github/callback"
    microsoft_oauth_redirect_url: str = "http://localhost:8000/api/v1/auth/oauth/microsoft/callback"
    
    frontend_url: str = "http://localhost:3000"
    backend_url: str = "http://localhost:8000"


    class Config:
        env_file = ".env"
        extra = "ignore"

    def is_provider_configured(self, provider: str) -> bool:
        """Check if a provider is properly configured."""
        if provider == "google":
            return bool(self.google_client_id and self.google_client_secret)
        elif provider == "github":
            return bool(self.github_client_id and self.github_client_secret)
        elif provider == "microsoft":
            return bool(self.microsoft_client_id and self.microsoft_client_secret)
        return False
    
    def get_redirect_url(self, provider: str) -> str:
        """Get the redirect URL for a specific provider."""
        if provider == "google":
            return self.google_oauth_redirect_url
        elif provider == "github":
            return self.github_oauth_redirect_url
        elif provider == "microsoft":
            return self.microsoft_oauth_redirect_url
        else:
            raise ValueError(f"Unsupported provider: {provider}")


# OAuth provider configurations
OAUTH_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "google": {
        "authorize_url": "https://accounts.google.com/o/oauth2/auth",
        "access_token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scopes": ["openid", "email", "profile"],
    },
    "github": {
        "authorize_url": "https://github.com/login/oauth/authorize",
        "access_token_url": "https://github.com/login/oauth/access_token",
        "userinfo_url": "https://api.github.com/user",
        "scopes": ["user:email"],
    },
    "microsoft": {
        "authorize_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "access_token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
        "scopes": ["openid", "email", "profile"],
    }
}