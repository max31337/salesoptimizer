from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from uuid import UUID
from datetime import datetime

from api.dependencies.auth import get_current_user_from_cookie
from application.use_cases.profile_update_use_cases import ProfileUpdateUseCase
from application.dtos.user_dto import (
    UpdateProfileRequest,
    UpdateProfileByAdminRequest,
    UserProfileResponse,
    ProfileUpdatePendingResponse
)
from application.dtos.organization_dto import OrganizationResponse, OrganizationInfoResponse
from domain.organization.entities.user import User
from domain.organization.services.tenant_service import TenantService
from infrastructure.dependencies.service_container import get_profile_update_use_case, get_tenant_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=UserProfileResponse)
async def get_my_profile(
    current_user: User = Depends(get_current_user_from_cookie),
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


@router.get("/organization", response_model=OrganizationInfoResponse)
async def get_organization_info(
    current_user: User = Depends(get_current_user_from_cookie),
    tenant_service: TenantService = Depends(get_tenant_service)
):
    """Get current user's organization information."""
    try:
        if not current_user.tenant_id:
            return OrganizationInfoResponse(
                organization=None, 
                message="User not associated with any organization"
            )
        
        # Get tenant from service using proper DDD architecture
        tenant = await tenant_service.get_tenant_by_id(current_user.tenant_id)
        
        if not tenant:
            return OrganizationInfoResponse(
                organization=None, 
                message="Organization not found"
            )
        # Convert tenant entity to response DTO
        organization_response = OrganizationResponse(
            id=str(tenant.id.value),
            name=tenant.name.value,
            slug=tenant.slug,
            subscription_tier=tenant.subscription_tier,
            is_active=tenant.is_active,
            owner_id=str(tenant.owner_id.value) if tenant.owner_id else None,
            settings=tenant.settings,
            created_at=tenant.created_at or datetime.now(),
            updated_at=tenant.updated_at or datetime.now()
        )
        
        return OrganizationInfoResponse(organization=organization_response)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch organization information")


@router.get("/{user_id}", response_model=UserProfileResponse)
async def get_user_profile(
    user_id: UUID,
    current_user: User = Depends(get_current_user_from_cookie),
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
    current_user: User = Depends(get_current_user_from_cookie),
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
    current_user: User = Depends(get_current_user_from_cookie),
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
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user_from_cookie),
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
    request: Request,
    current_user: User = Depends(get_current_user_from_cookie),
    profile_use_case: ProfileUpdateUseCase = Depends(get_profile_update_use_case)
):
    """Remove profile picture."""
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        result = await profile_use_case.delete_profile_picture(current_user.id.value)
        
        return JSONResponse(content=result)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
