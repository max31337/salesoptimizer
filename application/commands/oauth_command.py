from pydantic import BaseModel


class OAuthLoginCommand(BaseModel):
    """OAuth login command."""
    
    provider: str
    code: str
    redirect_uri: str


class OAuthAuthorizationCommand(BaseModel):
    """OAuth authorization URL command."""
    
    provider: str
    redirect_uri: str