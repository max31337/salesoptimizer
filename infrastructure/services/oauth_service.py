from typing import Dict, Any
import httpx
from urllib.parse import urlencode
from infrastructure.config.oauth_config import OAuthConfig, OAUTH_PROVIDERS


class OAuthService:
    """OAuth service for handling third-party authentication."""
    
    def __init__(self, config: OAuthConfig):
        self.config = config
    
    def get_authorization_url(self, provider: str, redirect_uri: str) -> str:
        """Get authorization URL for the specified provider."""
        if provider not in OAUTH_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = OAUTH_PROVIDERS[provider]
        
        if provider == "google":
            client_id = self.config.google_client_id
            if not client_id:
                raise ValueError("Google OAuth not configured")
            
            params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": "openid email profile",
                "response_type": "code",
                "access_type": "offline",
                "prompt": "consent"
            }
        
        elif provider == "github":
            client_id = self.config.github_client_id
            if not client_id:
                raise ValueError("GitHub OAuth not configured")
            
            params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": "user:email",
                "response_type": "code"
            }
        
        elif provider == "microsoft":
            client_id = self.config.microsoft_client_id
            if not client_id:
                raise ValueError("Microsoft OAuth not configured")
            
            params = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": "openid email profile",
                "response_type": "code"
            }
        
        else:
            raise ValueError(f"Provider {provider} not implemented")
        
        query_string = urlencode(params)
        return f"{provider_config['authorize_url']}?{query_string}"
    
    async def exchange_code_for_token(self, provider: str, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        if provider not in OAUTH_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = OAUTH_PROVIDERS[provider]
        
        if provider == "google":
            client_id = self.config.google_client_id
            client_secret = self.config.google_client_secret
            
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
        
        elif provider == "github":
            client_id = self.config.github_client_id
            client_secret = self.config.github_client_secret
            
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "redirect_uri": redirect_uri
            }
        
        elif provider == "microsoft":
            client_id = self.config.microsoft_client_id
            client_secret = self.config.microsoft_client_secret
            
            data = {
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": redirect_uri
            }
        
        else:
            raise ValueError(f"Token exchange for {provider} not implemented")
        
        async with httpx.AsyncClient() as client:
            headers = {"Accept": "application/json"}
            if provider == "github":
                headers["Accept"] = "application/vnd.github+json"
            
            response = await client.post(
                provider_config["access_token_url"],
                data=data,
                headers=headers
            )
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, provider: str, token: Dict[str, Any]) -> Dict[str, Any]:
        """Get user information using the access token."""
        if provider not in OAUTH_PROVIDERS:
            raise ValueError(f"Unsupported provider: {provider}")
        
        provider_config = OAUTH_PROVIDERS[provider]
        access_token = token.get("access_token")
        
        if not access_token:
            raise ValueError("No access token found")
        
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            if provider == "github":
                headers["Accept"] = "application/vnd.github+json"
            
            response = await client.get(
                provider_config["userinfo_url"],
                headers=headers
            )
            response.raise_for_status()
            user_data = response.json()
            
            # Normalize user data across providers
            if provider == "github":
                # GitHub might need email from separate endpoint
                if not user_data.get("email"):
                    email_response = await client.get(
                        "https://api.github.com/user/emails",
                        headers=headers
                    )
                    emails = email_response.json()
                    primary_email = next((e["email"] for e in emails if e["primary"]), None)
                    user_data["email"] = primary_email
            
            return user_data