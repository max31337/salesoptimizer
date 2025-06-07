from pathlib import Path
from typing import Optional, Dict, Any, Union, List
from uuid import UUID

from domain.organization.services.profile_update_service import ProfileUpdateService
from domain.organization.value_objects.email import Email
from domain.organization.value_objects.user_id import UserId
from domain.organization.repositories.user_repository import UserRepository
from domain.organization.repositories.profile_update_request_repository import ProfileUpdateRequestRepository
from application.dtos.user_dto import (
    UpdateProfileRequest,
    UpdateProfileByAdminRequest, 
    UserProfileResponse,
    ProfileUpdatePendingResponse
)


class ProfileUpdateUseCase:
    """Use case for handling profile updates."""
    
    def __init__(
        self,
        user_repository: UserRepository,
        profile_service: ProfileUpdateService,
        profile_update_request_repository: ProfileUpdateRequestRepository
    ):
        self.user_repository = user_repository
        self.profile_service = profile_service
        self.profile_update_request_repository = profile_update_request_repository

    async def get_user_profile(self, user_id: UUID) -> UserProfileResponse:
        """Get user profile information."""
        user = await self.user_repository.get_by_id(UserId(user_id))
        if not user:
            raise ValueError("User not found")
        
        return UserProfileResponse(
            user_id=str(user.id.value) if user.id else str(user_id),
            email=user.email.value,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            full_name=user.full_name,
            phone=user.phone,
            profile_picture_url=user.profile_picture_url,
            bio=user.bio,
            role=user.role.value,
            status=user.status.value,
            is_email_verified=user.is_email_verified,
            last_login=user.last_login,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    async def update_own_profile(
        self,
        user_id: UUID,
        request: UpdateProfileRequest
    ) -> Union[UserProfileResponse, ProfileUpdatePendingResponse]:
        """Update user's own profile."""
        
        user = await self.user_repository.get_by_id(UserId(user_id))
        if not user:
            raise ValueError("User not found")
        
        if user.id is None:
            raise ValueError("User ID cannot be None")
        
        # Validate the update
        validation = self.profile_service.validate_profile_update(
            user=user,
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            bio=request.bio,
            profile_picture_url=request.profile_picture_url
        )
        
        if not validation["is_valid"]:
            raise ValueError(f"Validation failed: {', '.join(validation['errors'])}")
        
        # Determine update strategy
        strategy = self.profile_service.determine_update_strategy(user=user, email=None)
        
        if strategy == "direct":
            # Update directly
            user.update_profile(
                first_name=request.first_name,
                last_name=request.last_name,
                phone=request.phone,
                bio=request.bio,
                profile_picture_url=request.profile_picture_url
            )
            
            await self.user_repository.update(user)
            
            return await self.get_user_profile(user_id)
        
        else:  # requires_approval
            # Create pending update record
            changes: Dict[str, Any] = {}
            if request.first_name is not None:
                changes["first_name"] = request.first_name
            if request.last_name is not None:
                changes["last_name"] = request.last_name
            if request.phone is not None:
                changes["phone"] = request.phone
            if request.bio is not None:
                changes["bio"] = request.bio
            if request.profile_picture_url is not None:
                changes["profile_picture_url"] = request.profile_picture_url
            
            # Check if there's already a pending request for this user
            existing_request = await self.profile_update_request_repository.get_pending_for_user(user.id)
            if existing_request:
                raise ValueError("There is already a pending profile update request for this user")
            
            # Create and save the profile update request
            profile_request = self.profile_service.create_profile_update_request(
                user=user,
                requested_by=user,
                changes=changes
            )
            
            await self.profile_update_request_repository.save(profile_request)
            
            return ProfileUpdatePendingResponse(
                message="Profile update request submitted for approval",
                requires_approval=True,
                pending_changes=changes
            )

    async def update_user_profile_by_admin(
        self,
        admin_user_id: UUID,
        target_user_id: UUID,
        request: UpdateProfileByAdminRequest
    ) -> UserProfileResponse:
        """Update user profile by admin (super_admin or org_admin)."""
        
        # Get admin user
        admin_user = await self.user_repository.get_by_id(UserId(admin_user_id))
        if not admin_user:
            raise ValueError("Admin user not found")
        
        # Check admin permissions
        if not self.profile_service.can_update_profile_directly(admin_user):
            raise ValueError("Insufficient permissions to update user profiles")
        
        # Get target user
        target_user = await self.user_repository.get_by_id(UserId(target_user_id))
        if not target_user:
            raise ValueError("Target user not found")
        
        # Validate the update
        validation = self.profile_service.validate_profile_update(
            user=target_user,
            first_name=request.first_name,
            last_name=request.last_name,
            email=request.email,
            phone=request.phone,
            bio=request.bio,
            profile_picture_url=request.profile_picture_url
        )
        
        if not validation["is_valid"]:
            raise ValueError(f"Validation failed: {', '.join(validation['errors'])}")
        
        # Update profile directly
        target_user.update_profile(
            first_name=request.first_name,
            last_name=request.last_name,
            phone=request.phone,
            bio=request.bio,
            profile_picture_url=request.profile_picture_url
        )
        
        # Update email if provided and allowed
        if request.email is not None:
            if not self.profile_service.can_update_email_directly(admin_user):
                raise ValueError("Insufficient permissions to update email")
            target_user.email = Email(request.email)
        
        await self.user_repository.update(target_user)
        
        return await self.get_user_profile(target_user_id)

    async def approve_profile_update_request(
        self,
        admin_user_id: UUID,
        request_id: UUID,
        reason: Optional[str] = None
    ) -> UserProfileResponse:
        """Approve a profile update request."""
        
        # Get admin user
        admin_user = await self.user_repository.get_by_id(UserId(admin_user_id))
        if not admin_user:
            raise ValueError("Admin user not found")
        
        if admin_user.id is None:
            raise ValueError("Admin user ID cannot be None")
        
        # Check admin permissions
        if not self.profile_service.can_update_profile_directly(admin_user):
            raise ValueError("Insufficient permissions to approve profile updates")
        
        # Get the profile update request
        profile_request = await self.profile_update_request_repository.get_by_id(request_id)
        if not profile_request:
            raise ValueError("Profile update request not found")
        
        if not profile_request.is_pending():
            raise ValueError("Profile update request is not pending")
        
        # Get the target user
        target_user = await self.user_repository.get_by_id(profile_request.user_id)
        if not target_user:
            raise ValueError("Target user not found")
        
        # Apply the changes
        changes = profile_request.requested_changes
        target_user.update_profile(
            first_name=changes.get("first_name"),
            last_name=changes.get("last_name"),
            phone=changes.get("phone"),
            bio=changes.get("bio"),
            profile_picture_url=changes.get("profile_picture_url")
        )
        
        # Update email if provided
        if "email" in changes:
            target_user.email = Email(changes["email"])
        
        # Approve the request
        profile_request.approve(admin_user.id, reason)
        
        # Save both the user and the request
        await self.user_repository.update(target_user)
        await self.profile_update_request_repository.update(profile_request)
        
        return await self.get_user_profile(profile_request.user_id.value)

    async def reject_profile_update_request(
        self,
        admin_user_id: UUID,
        request_id: UUID,
        reason: str
    ) -> Dict[str, Any]:
        """Reject a profile update request."""
        
        # Get admin user
        admin_user = await self.user_repository.get_by_id(UserId(admin_user_id))
        if not admin_user:
            raise ValueError("Admin user not found")
        
        if admin_user.id is None:
            raise ValueError("Admin user ID cannot be None")
        
        # Check admin permissions
        if not self.profile_service.can_update_profile_directly(admin_user):
            raise ValueError("Insufficient permissions to reject profile updates")
        
        # Get the profile update request
        profile_request = await self.profile_update_request_repository.get_by_id(request_id)
        if not profile_request:
            raise ValueError("Profile update request not found")
        
        if not profile_request.is_pending():
            raise ValueError("Profile update request is not pending")
        
        # Reject the request
        profile_request.reject(admin_user.id, reason)
        
        # Save the request
        await self.profile_update_request_repository.update(profile_request)
        
        return {
            "message": "Profile update request rejected",
            "reason": reason,
            "rejected_at": profile_request.updated_at
        }

    async def get_pending_profile_update_requests(
        self,
        admin_user_id: UUID,
        tenant_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get all pending profile update requests for a tenant."""
        
        # Get admin user
        admin_user = await self.user_repository.get_by_id(UserId(admin_user_id))
        if not admin_user:
            raise ValueError("Admin user not found")
        
        # Check admin permissions
        if not self.profile_service.can_update_profile_directly(admin_user):
            raise ValueError("Insufficient permissions to view pending requests")
        
        # Get pending requests
        requests = await self.profile_update_request_repository.get_pending_requests_for_approval(tenant_id)
        
        result: List[Dict[str, Any]] = []
        for request in requests:
            # Get user details
            user = await self.user_repository.get_by_id(request.user_id)
            if user:
                result.append({
                    "request_id": str(request.id),
                    "user_id": str(request.user_id.value),
                    "user_name": user.full_name,
                    "user_email": user.email.value,
                    "requested_changes": request.requested_changes,
                    "requested_at": request.created_at,
                    "requested_by_id": str(request.requested_by_id.value)                })
        
        return result    
    
    async def upload_profile_picture(
        self,
        user_id: UUID,
        file_data: bytes,
        filename: str,
        content_type: str
    ) -> Dict[str, Any]:
        """Upload profile picture for user."""
        
        user = await self.user_repository.get_by_id(UserId(user_id))
        if not user:
            raise ValueError("User not found")
        
        if user.id is None:
            raise ValueError("User ID cannot be None")
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if len(file_data) > max_size:
            raise ValueError("File size too large. Maximum allowed size is 5MB.")
        
        # Create uploads directory if it doesn't exist
        
        # Get the project root directory
        project_root = Path(__file__).parent.parent.parent
        uploads_dir = project_root / "uploads" / "profile_pictures"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_extension = Path(filename).suffix.lower()
        if not file_extension:
            # Default to jpg if no extension
            file_extension = '.jpg'
        
        unique_filename = f"{user_id}_{uuid.uuid4().hex[:8]}{file_extension}"
        file_path = uploads_dir / unique_filename
          # Save the file
        with open(file_path, 'wb') as f:
            f.write(file_data)
        
        # Create the URL path (relative to the API server)
        profile_picture_url = f"/uploads/profile_pictures/{unique_filename}"
        
        # Check if user can update profile directly
        if self.profile_service.can_update_profile_directly(user):
            # Update directly for super admin and org admin
            user.update_profile(profile_picture_url=profile_picture_url)
            await self.user_repository.update(user)
            
            return {
                "message": "Profile picture uploaded successfully",
                "profile_picture_url": profile_picture_url,
                "requires_approval": False
            }
        else:
            # Go through approval workflow for other users
            request = UpdateProfileRequest(profile_picture_url=profile_picture_url)
            result = await self.update_own_profile(user_id, request)
            
            return {                "message": "Profile picture uploaded successfully",
                "profile_picture_url": profile_picture_url,
                "requires_approval": isinstance(result, ProfileUpdatePendingResponse)
            }

    async def delete_profile_picture(
        self,
        user_id: UUID
    ) -> Dict[str, Any]:
        """Delete user's profile picture."""
        
        user = await self.user_repository.get_by_id(UserId(user_id))
        if not user:
            raise ValueError("User not found")
        
        if user.id is None:
            raise ValueError("User ID cannot be None")
        
        # Get the current profile picture URL
        current_picture_url = user.profile_picture_url
        
        # Check if user can update profile directly
        if self.profile_service.can_update_profile_directly(user):
            # Update directly for super admin and org admin
            user.update_profile(profile_picture_url=None)
            await self.user_repository.update(user)
            
            # If there was a picture, try to delete the file
            if current_picture_url and current_picture_url.startswith("/uploads/profile_pictures/"):
                try:
                    from pathlib import Path
                    project_root = Path(__file__).parent.parent.parent
                    file_path = project_root / current_picture_url.lstrip("/")
                    
                    if file_path.exists():
                        file_path.unlink()  # Delete the file
                except Exception as e:
                    # Log the error but don't fail the operation
                    print(f"Failed to delete profile picture file: {e}")
            
            return {
                "message": "Profile picture removed successfully",
                "requires_approval": False
            }
        else:
            # Go through approval workflow for other users
            request = UpdateProfileRequest(profile_picture_url=None)
            result = await self.update_own_profile(user_id, request)
            
            return {
                "message": "Profile picture removal submitted for approval",
                "requires_approval": isinstance(result, ProfileUpdatePendingResponse)
            }
