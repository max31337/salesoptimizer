from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from uuid import UUID

from api.dependencies.auth import get_current_user
from application.use_cases.profile_update_use_cases import ProfileUpdateUseCase
from application.dtos.user_dto import (
    UpdateProfileRequest,
    UpdateProfileByAdminRequest,
    UserProfileResponse,
    ProfileUpdatePendingResponse
)
from domain.organization.entities.user import User
from infrastructure.dependencies.service_container import get_profile_update_use_case

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user),
    profile_use_case: ProfileUpdateUseCase = Depends(get_profile_update_use_case)
):
    """Get current user's profile."""
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID is required")
        return await profile_use_case.get_user_profile(current_user.id.value)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    profile_use_case: ProfileUpdateUseCase = Depends(get_profile_update_use_case)
):
    """Get user profile by ID (admin only)."""
    
    # Check if current user is admin
    if current_user.role.value not in ['super_admin', 'org_admin']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        return await profile_use_case.get_user_profile(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/me")
async def update_my_profile(
    request: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    profile_use_case: ProfileUpdateUseCase = Depends(get_profile_update_use_case)
):
    """Update current user's profile."""
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        result = await profile_use_case.update_own_profile(current_user.id.value, request)
        
        # Check if result is pending approval
        if isinstance(result, ProfileUpdatePendingResponse):
            return JSONResponse(
                status_code=202,  # Accepted
                content=result.model_dump()
            )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/{user_id}", response_model=UserProfileResponse)
async def update_user_profile_by_admin(
    user_id: UUID,
    request: UpdateProfileByAdminRequest,
    current_user: User = Depends(get_current_user),
    profile_use_case: ProfileUpdateUseCase = Depends(get_profile_update_use_case)
):
    """Update user profile by admin."""
    
    # Check if current user is admin
    if current_user.role.value not in ['super_admin', 'org_admin']:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        return await profile_use_case.update_user_profile_by_admin(
            current_user.id.value, user_id, request
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/me/profile-picture")
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    profile_use_case: ProfileUpdateUseCase = Depends(get_profile_update_use_case)
):
    """Upload profile picture."""
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail="Invalid file type. Only JPEG, PNG, GIF, and WebP are allowed."
        )
    
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Read file data
        file_data = await file.read()
        
        result = await profile_use_case.upload_profile_picture(
            current_user.id.value,
            file_data,
            file.filename or "profile_picture",
            file.content_type or "image/jpeg"
        )
        
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/me/profile-picture")
async def remove_profile_picture(
    current_user: User = Depends(get_current_user),
    profile_use_case: ProfileUpdateUseCase = Depends(get_profile_update_use_case)
):
    """Remove profile picture."""
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        # Update profile to remove picture
        request = UpdateProfileRequest(profile_picture_url=None)
        await profile_use_case.update_own_profile(current_user.id.value, request)
        
        return JSONResponse(content={"message": "Profile picture removed successfully"})
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
