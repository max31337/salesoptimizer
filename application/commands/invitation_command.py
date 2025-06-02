from pydantic import BaseModel, EmailStr


class CreateInvitationCommand(BaseModel):
    """Create invitation command."""
    
    email: EmailStr
    organization_name: str