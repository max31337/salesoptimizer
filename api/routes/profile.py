from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Request
from fastapi.responses import JSONResponse
from uuid import UUID
from datetime import datetime
from typing import Union

from api.dependencies.auth import get_current_user_from_cookie
from application.use_cases.profile_update_use_cases import ProfileUpdateUseCase
from application.dtos.user_dto import (
    UpdateProfileRequest,
    UpdateProfileByAdminRequest,
    UserProfileResponse,
    UserProfilePublicResponse,
    UserProfileAdminResponse,
    ProfileUpdatePendingResponse,
    TeamInfoResponse
)
from application.dtos.organization_dto import (
    OrganizationResponse, 
    OrganizationInfoResponse,
    OrganizationPublicResponse,
    OrganizationInfoPublicResponse
)
from domain.organization.entities.user import User
from domain.organization.services.tenant_service import TenantService
from domain.organization.services.team_service import TeamService
from infrastructure.dependencies.service_container import get_profile_update_use_case, get_tenant_service, get_team_service

router = APIRouter(prefix="/profile", tags=["profile"])


@router.get("/me", response_model=Union[UserProfileAdminResponse, UserProfilePublicResponse])
async def get_my_profile(
    current_user: User = Depends(get_current_user_from_cookie),
    profile_use_case: ProfileUpdateUseCase = Depends(get_profile_update_use_case),
    team_service: TeamService = Depends(get_team_service)
):
    """Get current user's profile with role-based information disclosure."""
    try:
        if current_user.id is None:
            raise HTTPException(status_code=400, detail="User ID is required")
        
        profile_data = await profile_use_case.get_user_profile(current_user.id.value)
          # Get team information if user has a team
        team_info = None
        if current_user.team_id:
            try:
                team_data = await team_service.get_team_by_id(current_user.team_id)
                if team_data:
                    # Get member count for the team
                    member_count = await team_service.get_team_member_count(current_user.team_id)
                    
                    # Get manager name if exists
                    manager_name = None
                    if team_data.get("manager_id"):
                        manager_model = await team_service.get_user_by_id(team_data["manager_id"])
                        if manager_model:
                            manager_name = getattr(manager_model, 'full_name', None) or manager_model.username
                    
                    team_info = TeamInfoResponse(
                        id=team_data["id"],
                        name=team_data["name"],
                        description=team_data.get("description"),
                        member_count=member_count,
                        manager_name=manager_name,
                        is_active=team_data["is_active"]
                    )
            except Exception as e:
                # Log error but don't fail the entire request
                print(f"Error fetching team info: {e}")
        
        # Return different response models based on user role
        if current_user.role.value in ['super_admin']:
            # Admins get full profile with UUIDs and technical details
            return UserProfileAdminResponse(
                **profile_data.model_dump(),
                tenant_id=str(current_user.tenant_id) if current_user.tenant_id else None,
                team_id=str(current_user.team_id) if current_user.team_id else None,
                team_info=team_info
            )
        else:
            # Regular users get public profile without UUIDs
            profile_dict = profile_data.model_dump()
            # Remove user_id for regular users
            profile_dict.pop('user_id', None)
            return UserProfilePublicResponse(**profile_dict, team_info=team_info)
            
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/organization", response_model=Union[OrganizationInfoResponse, OrganizationInfoPublicResponse])
async def get_organization_info(
    current_user: User = Depends(get_current_user_from_cookie),
    tenant_service: TenantService = Depends(get_tenant_service)
):
    """Get current user's organization information with role-based display."""
    try:
        if not current_user.tenant_id:
            # Return appropriate response based on user role
            if current_user.role.value in ['super_admin', 'org_admin']:
                return OrganizationInfoResponse(
                    organization=None, 
                    message="User not associated with any organization"
                )
            else:
                return OrganizationInfoPublicResponse(
                    organization=None, 
                    message="User not associated with any organization"
                )
        
        # Get tenant from service using proper DDD architecture
        tenant = await tenant_service.get_tenant_by_id(current_user.tenant_id)
        
        if not tenant:
            # Return appropriate response based on user role
            if current_user.role.value in ['super_admin', 'org_admin']:
                return OrganizationInfoResponse(
                    organization=None, 
                    message="Organization not found"
                )
            else:
                return OrganizationInfoPublicResponse(
                    organization=None, 
                    message="Organization not found"
                )
        
        # Return different response models based on user role
        if current_user.role.value in ['super_admin', 'org_admin']:
            # Admins get full organization details with UUIDs
            organization_response = OrganizationResponse(
                id=str(tenant.id.value) if tenant.id is not None else "",
                name=tenant.name,
                slug=tenant.slug or "",
                subscription_tier=tenant.subscription_tier or "",
                is_active=tenant.is_active,
                owner_id=str(tenant.owner_id.value) if tenant.owner_id else None,
                settings=tenant.settings,
                created_at=tenant.created_at or datetime.now(),
                updated_at=tenant.updated_at or datetime.now()
            )
            return OrganizationInfoResponse(organization=organization_response)
        else:
            # Regular users get public organization details without UUIDs
            organization_response = OrganizationPublicResponse(
                name=tenant.name,
                subscription_tier=tenant.subscription_tier or "",
                is_active=tenant.is_active,
                created_at=tenant.created_at or datetime.now(),
                updated_at=tenant.updated_at or datetime.now()
            )
            return OrganizationInfoPublicResponse(organization=organization_response)
        
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
