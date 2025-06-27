from dataclasses import dataclass
from typing import Optional


@dataclass
class OrganizationRegistrationCommand:
    """Command for self-serve organization registration."""
    
    # Organization details
    organization_name: str
    organization_slug: Optional[str]
    industry: str
    organization_size: str
    website: Optional[str]
    
    # Admin user details
    first_name: str
    last_name: str
    email: str
    password: str
    job_title: str
    
    # Subscription details
    subscription_tier: str  # trial, basic, pro
    
    # Legal agreements
    accept_terms: bool
    accept_privacy: bool
    marketing_opt_in: bool = False
    
    def __post_init__(self):
        """Validate command data."""
        if not self.organization_name or not self.organization_name.strip():
            raise ValueError("Organization name is required")
        
        if not self.first_name or not self.first_name.strip():
            raise ValueError("First name is required")
            
        if not self.last_name or not self.last_name.strip():
            raise ValueError("Last name is required")
            
        if not self.email or not self.email.strip():
            raise ValueError("Email is required")
            
        if not self.password or len(self.password) < 8:
            raise ValueError("Password must be at least 8 characters")
            
        if self.subscription_tier not in ["trial", "basic", "pro"]:
            raise ValueError("Invalid subscription tier selection")

        if not self.accept_terms:
            raise ValueError("Terms of service must be accepted")
            
        if not self.accept_privacy:
            raise ValueError("Privacy policy must be accepted")
