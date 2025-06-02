from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateInvitationCommand:
    """Command to create an organization admin invitation with tenant."""
    
    email: str
    organization_name: str
    subscription_tier: str = "basic"
    slug: Optional[str] = None