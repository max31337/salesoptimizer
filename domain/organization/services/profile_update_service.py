from typing import Optional, Dict, Any
from typing import Optional, Dict, Any
from domain.organization.entities.user import User
from domain.organization.entities.profile_update_request import ProfileUpdateRequest, ProfileUpdateStatus

from domain.organization.value_objects.email import Email


class ProfileUpdateService:
    """Domain service for handling profile updates with approval workflow."""
    
    def can_update_profile_directly(self, user: User) -> bool:
        """Check if user can update their profile without approval."""
        # Super admin and org admin can update directly
        return user.role.value in ['super_admin', 'org_admin']
    
    def can_update_email_directly(self, user: User) -> bool:
        """Check if user can update email without approval."""
        # Only super admin and org admin can update email directly
        return user.role.value in ['super_admin', 'org_admin']
    
    def validate_profile_update(
        self, 
        user: User,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        bio: Optional[str] = None,
        profile_picture_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Validate profile update and return validation result."""
        
        errors: list[str] = []
        
        # Validate first name
        if first_name is not None:
            if not first_name or not first_name.strip():
                errors.append("First name cannot be empty")
        
        # Validate last name
        if last_name is not None:
            if not last_name or not last_name.strip():
                errors.append("Last name cannot be empty")
        
        # Validate email format if provided
        if email is not None:
            try:
                Email(email)
            except ValueError as e:
                errors.append(f"Invalid email format: {str(e)}")
        
        # Validate phone format (basic validation)
        if phone is not None and phone:
            phone = phone.strip()
            if len(phone) > 20:
                errors.append("Phone number is too long")
        
        # Validate bio length
        if bio is not None and bio:
            if len(bio) > 1000:
                errors.append("Bio is too long (max 1000 characters)")
        
        # Validate profile picture URL
        if profile_picture_url is not None and profile_picture_url:
            if len(profile_picture_url) > 500:
                errors.append("Profile picture URL is too long")
        
        return {
            "is_valid": len(errors) == 0,
            "errors": errors
        }
    
    def determine_update_strategy(
        self, 
        user: User,
        email: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Determine if update should be direct or require approval."""
        
        # If email is being updated
        if email is not None:
            if not self.can_update_email_directly(user):
                return "requires_approval"
        
        # For other profile fields
        if not self.can_update_profile_directly(user):
            return "requires_approval"
        
        return "direct"
    
    def create_profile_update_request(
        self,
        user: User,
        requested_by: User,
        changes: Dict[str, Any]
    ) -> ProfileUpdateRequest:
        """Create a profile update request for approval."""
        
        if user.id is None:
            raise ValueError("User ID cannot be None")
        if requested_by.id is None:
            raise ValueError("Requested by user ID cannot be None")
        
        return ProfileUpdateRequest(
            id=None,
            user_id=user.id,
            requested_by_id=requested_by.id,
            requested_changes=changes,
            status=ProfileUpdateStatus.PENDING
        )
